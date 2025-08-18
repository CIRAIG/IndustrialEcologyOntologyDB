-- =========================================================
-- LCA / ACL schema bootstrap (PostgreSQL)
-- =========================================================

-- 1) Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;        -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- 2) Schéma
CREATE SCHEMA IF NOT EXISTS lca;
SET search_path = lca, public;

-- 3) ENUMs (optionnels mais utiles)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'flow_role') THEN
    CREATE TYPE flow_role AS ENUM ('input','output');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'good_type') THEN
    CREATE TYPE good_type AS ENUM ('good','proxy');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'dsv_status') THEN
    CREATE TYPE dsv_status AS ENUM ('draft','reviewed','published');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tec_basis') THEN
    CREATE TYPE tec_basis AS ENUM ('per_FU','per_property','per_flow');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'impact_level') THEN
    CREATE TYPE impact_level AS ENUM ('midpoint','endpoint');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'uncertainty_kind') THEN
    CREATE TYPE uncertainty_kind AS ENUM ('lognormal','normal','triangular','uniform');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_level') THEN
    CREATE TYPE risk_level AS ENUM ('low','med','high');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fic_kind') THEN
    CREATE TYPE fic_kind AS ENUM ('impact','elementary_flow','cost');
  END IF;
END$$;

-- 4) Référentiels communs
CREATE TABLE dimension (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE unit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  symbol TEXT NOT NULL,
  dimension_id UUID REFERENCES dimension(id) ON DELETE SET NULL
);

CREATE TABLE taxonomy (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE term (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  taxonomy_id UUID NOT NULL REFERENCES taxonomy(id) ON DELETE CASCADE,
  code TEXT NOT NULL,
  label TEXT NOT NULL,
  parent_id UUID REFERENCES term(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX term_tax_code_ux ON term(taxonomy_id, code);

CREATE TABLE region (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL,
  label TEXT NOT NULL,
  parent_id UUID REFERENCES region(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX region_code_ux ON region(code);

CREATE TABLE source (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name TEXT NOT NULL,
  row_id UUID NOT NULL,
  field_name TEXT NOT NULL,
  title TEXT,
  year INT,
  doi_or_url TEXT,
  citation TEXT
);

CREATE INDEX source_lookup_ix ON source(table_name, row_id, field_name);

CREATE TABLE term_assignment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  term_id UUID NOT NULL REFERENCES term(id) ON DELETE CASCADE,
  table_name TEXT NOT NULL,
  row_id UUID NOT NULL,
  field_name TEXT NOT NULL
);

CREATE INDEX ta_lookup_ix ON term_assignment(term_id, table_name, row_id, field_name);

-- 5) Gouvernance datasets
CREATE TABLE study (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE dataset (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  study_id UUID REFERENCES study(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE dataset_version (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_id UUID NOT NULL REFERENCES dataset(id) ON DELETE CASCADE,
  version_tag TEXT NOT NULL,
  valid_from DATE,
  valid_to DATE,
  region_id UUID REFERENCES region(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status dsv_status NOT NULL DEFAULT 'draft'
);

CREATE UNIQUE INDEX dsv_unique_ux ON dataset_version(dataset_id, version_tag);

-- 6) Noyau matière
CREATE TABLE good (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  classification_id UUID REFERENCES term(id) ON DELETE SET NULL
);

CREATE TABLE transformable_entity ( -- substance
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL
);

CREATE TABLE conserved_entity ( -- cprop
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL
);

CREATE TABLE intensive_property (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  unit_id UUID REFERENCES unit(id) ON DELETE RESTRICT,
  name TEXT NOT NULL
);

CREATE TABLE intensive_property_value (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  value NUMERIC NOT NULL,
  intensive_property_id UUID NOT NULL REFERENCES intensive_property(id) ON DELETE CASCADE,
  table_name TEXT NOT NULL,
  row_id UUID NOT NULL,
  field_name TEXT NOT NULL
);

CREATE INDEX ipv_lookup_ix ON intensive_property_value(intensive_property_id, table_name, row_id, field_name);

-- BOM : good in good
CREATE TABLE good_contains_good (
  parent_good_id UUID NOT NULL REFERENCES good(id) ON DELETE CASCADE,
  child_good_id UUID NOT NULL REFERENCES good(id) ON DELETE CASCADE,
  amount NUMERIC NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE RESTRICT,
  PRIMARY KEY (parent_good_id, child_good_id)
);

-- Good contains substance
CREATE TABLE good_contains_transformable_entity (
  good_id UUID NOT NULL REFERENCES good(id) ON DELETE CASCADE,
  transformable_entity_id UUID NOT NULL REFERENCES transformable_entity(id) ON DELETE CASCADE,
  amount NUMERIC NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE RESTRICT,
  PRIMARY KEY (good_id, transformable_entity_id)
);

-- Substance contains conserved entity (stoichiometry)
CREATE TABLE transformable_entity_contain_conserved_entity (
  transformable_entity_id UUID NOT NULL REFERENCES transformable_entity(id) ON DELETE CASCADE,
  conserved_entity_id UUID NOT NULL REFERENCES conserved_entity(id) ON DELETE CASCADE,
  ratio NUMERIC NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE RESTRICT,
  PRIMARY KEY (transformable_entity_id, conserved_entity_id)
);

-- 7) Processus & flux
CREATE TABLE process (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_version_id UUID NOT NULL REFERENCES dataset_version(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  region_id UUID REFERENCES region(id) ON DELETE SET NULL
);

CREATE TABLE custom_process_parameter (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  value TEXT NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE SET NULL,
  note TEXT
);

CREATE TABLE economic_flow (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  good_type good_type NOT NULL DEFAULT 'good',
  good_id UUID REFERENCES good(id) ON DELETE SET NULL,
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  role flow_role NOT NULL,
  is_reference_product BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX pflow_proc_role_ix ON economic_flow(process_id, role);
CREATE INDEX pflow_ref_ix ON economic_flow(process_id, is_reference_product);

CREATE TABLE measurement (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  economic_flow_id UUID NOT NULL REFERENCES economic_flow(id) ON DELETE CASCADE,
  value TEXT NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE SET NULL,
  note TEXT
);

CREATE TABLE measurement_constraint (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  measurement_id UUID NOT NULL REFERENCES measurement(id) ON DELETE CASCADE,
  kind TEXT NOT NULL,      -- min|max|ratio|balance (libre)
  json_value JSONB NOT NULL,
  note TEXT
);

CREATE TABLE compartment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id UUID REFERENCES compartment(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE factor (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  classification_id UUID REFERENCES term(id) ON DELETE SET NULL
);

CREATE TABLE elementary_flow (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  classification_id UUID REFERENCES term(id) ON DELETE SET NULL,
  compartment_id UUID REFERENCES compartment(id) ON DELETE SET NULL,
  factor_id UUID REFERENCES factor(id) ON DELETE SET NULL
);

-- (Optionnel) relation n-n process ↔ elementary_flow si besoin explicite
CREATE TABLE process_elementary_flow (
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  elementary_flow_id UUID NOT NULL REFERENCES elementary_flow(id) ON DELETE CASCADE,
  PRIMARY KEY (process_id, elementary_flow_id)
);

-- relation n-n factor ↔ substance
CREATE TABLE factor_substance (
  factor_id UUID NOT NULL REFERENCES factor(id) ON DELETE CASCADE,
  transformable_entity_id UUID NOT NULL REFERENCES transformable_entity(id) ON DELETE CASCADE,
  PRIMARY KEY (factor_id, transformable_entity_id)
);

CREATE TABLE transfer_coefficient (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  cons_in_property_id UUID REFERENCES conserved_entity(id) ON DELETE SET NULL,
  trans_in_substance_id UUID REFERENCES transformable_entity(id) ON DELETE SET NULL,
  goods_in_id UUID REFERENCES good(id) ON DELETE SET NULL,
  trans_out_substance_id UUID REFERENCES transformable_entity(id) ON DELETE SET NULL,
  goods_out_id UUID REFERENCES good(id) ON DELETE SET NULL,
  value NUMERIC NOT NULL,
  order_index INT NOT NULL DEFAULT 0,
  note TEXT
);

CREATE TABLE technical_coefficient (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  determined_flow_role flow_role NOT NULL,    -- input|output|emission
  good_id UUID REFERENCES good(id) ON DELETE SET NULL,
  substance_id UUID REFERENCES transformable_entity(id) ON DELETE SET NULL,
  value NUMERIC NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE SET NULL,
  basis_type tec_basis NOT NULL DEFAULT 'per_FU',
  reference_property_id UUID REFERENCES intensive_property(id) ON DELETE SET NULL,
  order_index INT NOT NULL DEFAULT 0,
  functional BOOLEAN NOT NULL DEFAULT true,
  note TEXT,
  CHECK ( (good_id IS NOT NULL) <> (substance_id IS NOT NULL) )
);

-- 8) System model (réseau)
CREATE TABLE system_model (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_version_id UUID NOT NULL REFERENCES dataset_version(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  objective TEXT
);

CREATE TABLE system_node (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  system_model_id UUID NOT NULL REFERENCES system_model(id) ON DELETE CASCADE,
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  label TEXT
);

CREATE TABLE system_edge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_node_id UUID NOT NULL REFERENCES system_node(id) ON DELETE CASCADE,
  to_node_id UUID NOT NULL REFERENCES system_node(id) ON DELETE CASCADE,
  condition TEXT
);

-- 9) Incertitudes
CREATE TABLE measure_uncertainty (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name TEXT NOT NULL,
  row_id UUID NOT NULL,
  field_name TEXT NOT NULL,
  kind uncertainty_kind NOT NULL,
  distribution_params JSONB NOT NULL,
  note TEXT
);

CREATE INDEX mu_lookup_ix ON measure_uncertainty(table_name, row_id, field_name);

-- 10) Proxies
CREATE TABLE proxy_definition (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  good_id UUID NOT NULL REFERENCES good(id) ON DELETE CASCADE,
  similarity_score NUMERIC,
  risk_level risk_level,
  skip_flag BOOLEAN NOT NULL DEFAULT false,
  reason TEXT,
  method TEXT,
  note TEXT,
  valid_from TIMESTAMPTZ,
  valid_to TIMESTAMPTZ
);

CREATE TABLE proxy_measurement_adjustment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  measurement_id UUID NOT NULL REFERENCES measurement(id) ON DELETE CASCADE,
  factor NUMERIC NOT NULL DEFAULT 1,
  offset NUMERIC NOT NULL DEFAULT 0,
  note TEXT
);

-- 11) Impacts & facteurs de caractérisation
CREATE TABLE characterization_method (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  description TEXT,
  version TEXT
);

CREATE TABLE impact (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  method_id UUID NOT NULL REFERENCES characterization_method(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE SET NULL,
  time_horizon TEXT,
  level impact_level NOT NULL,
  description TEXT
);

CREATE TABLE characterization_factor (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  method_id UUID NOT NULL REFERENCES characterization_method(id) ON DELETE CASCADE,
  impact_id UUID NOT NULL REFERENCES impact(id) ON DELETE CASCADE,
  elementary_flow_id UUID NOT NULL REFERENCES elementary_flow(id) ON DELETE CASCADE,
  conversion_factor NUMERIC NOT NULL,
  note TEXT,
  UNIQUE (method_id, impact_id, elementary_flow_id)
);

-- 12) Background datasets & clusters
CREATE TABLE background_dataset (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  publisher TEXT,
  external_id TEXT,
  version TEXT,
  description TEXT
);

CREATE TABLE background_dataset_has_process (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  background_dataset_id UUID NOT NULL REFERENCES background_dataset(id) ON DELETE CASCADE,
  external_process_id TEXT NOT NULL,
  label TEXT,
  extra JSONB
);

CREATE UNIQUE INDEX bg_proc_ux ON background_dataset_has_process(background_dataset_id, external_process_id);

-- 13) Expérience / modèle de process / demande finale / bornes / contraintes / matching
CREATE TABLE experience (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  system_model_id UUID NOT NULL REFERENCES system_model(id) ON DELETE CASCADE,
  author TEXT,
  version TEXT,
  system_boundaries TEXT,
  objectives TEXT,
  function_desc TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE process_model (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  reference_flow_id UUID NOT NULL REFERENCES economic_flow(id) ON DELETE RESTRICT,
  label TEXT,
  note TEXT
);

CREATE UNIQUE INDEX process_model_unique_flow_ux ON process_model(process_id, reference_flow_id);

CREATE TABLE experience_generators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experience_id UUID NOT NULL REFERENCES experience(id) ON DELETE CASCADE,
  process_model_id UUID NOT NULL REFERENCES process_model(id) ON DELETE CASCADE,
  UNIQUE (experience_id, process_model_id)
);

CREATE TABLE final_demand (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experience_id UUID NOT NULL REFERENCES experience(id) ON DELETE CASCADE,
  good_id UUID NOT NULL REFERENCES good(id) ON DELETE RESTRICT,
  quantity NUMERIC NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE RESTRICT,
  note TEXT
);

CREATE TABLE process_bounds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experience_id UUID NOT NULL REFERENCES experience(id) ON DELETE CASCADE,
  process_id UUID NOT NULL REFERENCES process(id) ON DELETE CASCADE,
  economic_flow_id UUID NOT NULL REFERENCES economic_flow(id) ON DELETE RESTRICT,
  lower_bound NUMERIC,
  upper_bound NUMERIC,
  unit_id UUID REFERENCES unit(id) ON DELETE RESTRICT,
  note TEXT
);

CREATE TABLE factor_impact_constraints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experience_id UUID NOT NULL REFERENCES experience(id) ON DELETE CASCADE,
  kind fic_kind NOT NULL,
  impact_id UUID REFERENCES impact(id) ON DELETE SET NULL,
  elementary_flow_id UUID REFERENCES elementary_flow(id) ON DELETE SET NULL,
  quantity NUMERIC NOT NULL,
  unit_id UUID REFERENCES unit(id) ON DELETE SET NULL,
  note TEXT,
  CHECK (
    (kind = 'impact' AND impact_id IS NOT NULL AND elementary_flow_id IS NULL)
    OR
    (kind = 'elementary_flow' AND elementary_flow_id IS NOT NULL AND impact_id IS NULL)
    OR
    (kind = 'cost' AND impact_id IS NULL AND elementary_flow_id IS NULL)
  )
);

CREATE TABLE flow_background_match (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_flow_id UUID NOT NULL REFERENCES economic_flow(id) ON DELETE CASCADE,
  background_dataset_id UUID NOT NULL REFERENCES background_dataset(id) ON DELETE CASCADE,
  background_process_id TEXT NOT NULL,
  conversion_factor NUMERIC NOT NULL DEFAULT 1,
  note TEXT,
  UNIQUE (process_flow_id, background_dataset_id, background_process_id)
);

-- 14) Petites aides d’intégrité
-- Un seul flow de référence (is_reference_product) par process (optionnel mais utile)
CREATE UNIQUE INDEX one_ref_flow_per_process_ux
ON economic_flow(process_id)
WHERE is_reference_product;

-- 15) Index divers utiles
CREATE INDEX good_name_ix ON good USING GIN (to_tsvector('simple', name));
CREATE INDEX process_name_ix ON process USING GIN (to_tsvector('simple', name));
CREATE INDEX ef_name_ix ON elementary_flow USING GIN (to_tsvector('simple', name));
