# Référentiels communs

Les référentiels servent de fondations aux autres entités du modèle.  
Ils garantissent la cohérence des unités, classifications, et régions utilisées.

---

## Dimensions et unités

| Table | Description |
|--------|--------------|
| **dimension** | Définit les grandeurs physiques (masse, énergie, etc.). |
| **unit** | Liste des unités associées à une dimension donnée. |
| **measurement** | Stocke une valeur mesurée, associée à une unité et un flux de processus. |

---

## Taxonomies et termes

| Table | Description |
|--------|--------------|
| **taxonomy** | Définit une nomenclature (CPC, ISIC, interne, etc.). |
| **term** | Élément d’une taxonomie, avec hiérarchie optionnelle. |
| **term_assignment** | Lien entre un terme et un enregistrement d’une autre table (par exemple, un bien ou un processus). |

---

## Sources et régions

| Table | Description |
|--------|--------------|
| **source** | Référence bibliographique ou DOI associée à un champ d’une table. |
| **region** | Hiérarchie de régions (CH, RER, GLO, etc.), utilisée pour contextualiser les données. |
