from django.db import models


class Project(models.Model):
    name = models.CharField(
        max_length=256,
        default="New Project",
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name


class TermMixin(models.Model):
    """
    Mixin to add a ForeignKey to Term.
    Used for models that need to be associated with a Term.
    """

    terms = models.ManyToManyField(
        "Term",
        blank=True,
        related_name="%(class)s_terms",
        help_text="Terms associated with this entity.",
    )

    class Meta:
        abstract = True


class Dimension(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="dimensions",
    )

    name = models.CharField(
        max_length=128,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(
        max_length=128,
    )

    symbol = models.CharField(
        max_length=32,
        unique=True,
    )

    dimension = models.ForeignKey(
        Dimension,
        on_delete=models.CASCADE,
        related_name="units",
    )

    def __str__(self):
        return f"{self.dimension.name} - {self.name}"


class Taxonomy(models.Model):
    name = models.CharField(
        max_length=512,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taxonomy"
        verbose_name_plural = "Taxonomies"


class Term(models.Model):
    taxonomy = models.ForeignKey(
        Taxonomy,
        on_delete=models.CASCADE,
        related_name="terms",
    )

    name = models.CharField(
        max_length=512,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class ConservedEntity(TermMixin):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="conserved_entities",
    )

    name = models.CharField(
        max_length=512,
    )

    short_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Short name or symbol for the conserved entity (e.g., 'C' for Carbon).",
    )

    molar_mass = models.FloatField(
        null=True,
        blank=True,
        help_text="Molar mass of the conserved entity in g/mol.",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Conserved Entity"
        verbose_name_plural = "Conserved Entities"


class TransformableEntity(TermMixin):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="transformable_entities",
    )

    name = models.CharField(
        max_length=512,
    )

    short_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Short name or symbol for the transformable entity (e.g., 'CH4' for Methane).",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Transformable Entity"
        verbose_name_plural = "Transformable Entities"


class Good(TermMixin):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="goods",
    )

    name = models.CharField(
        max_length=512,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    reference_unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        help_text="Reference unit for the good.",
    )

    def __str__(self):
        return f"{self.name} ({self.project})"


class TransformableEntityContainConservedEntity(models.Model):

    conserved_entity = models.ForeignKey(
        ConservedEntity,
        on_delete=models.CASCADE,
        related_name="transformables",
    )

    transformable_entity = models.ForeignKey(
        TransformableEntity,
        on_delete=models.CASCADE,
        related_name="conserveds",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        help_text="Unit of the ratio.",
    )

    ratio = models.FloatField(
        help_text="Ratio of conserved entity per unit of transformable entity.",
    )


class GoodContainTransformableEntity(models.Model):

    good = models.ForeignKey(
        Good,
        on_delete=models.CASCADE,
        related_name="transformables",
    )

    transformable_entity = models.ForeignKey(
        TransformableEntity,
        on_delete=models.CASCADE,
        related_name="goods",
    )

    quantity = models.FloatField(
        help_text="Quantity of transformable entity in the good.",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        help_text="Unit of the quantity.",
    )


class GoodContainGood(models.Model):

    parent_good = models.ForeignKey(
        Good,
        on_delete=models.CASCADE,
        related_name="subgoods",
    )

    child_good = models.ForeignKey(
        Good,
        on_delete=models.CASCADE,
        related_name="supergoods",
    )

    quantity = models.FloatField(
        help_text="Quantity of child good in the parent good.",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        help_text="Unit of the quantity.",
    )


class Process(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="processes",
    )

    name = models.CharField(
        max_length=512,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Process"
        verbose_name_plural = "Processes"


class EconomicFlow(models.Model):

    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        related_name="economic_flows",
    )

    good = models.ForeignKey(
        Good,
        on_delete=models.CASCADE,
        related_name="economic_flows",
    )

    quantity = models.FloatField(
        help_text="Quantity of good in the economic flow.",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        help_text="Unit of the quantity.",
    )

    direction = models.CharField(
        max_length=10,
        choices=[("input", "Input"), ("output", "Output")],
        help_text="Indicates whether the good is an input to or an output from the process.",
    )

    is_byproduct = models.BooleanField(
        default=False,
        help_text="True if the good is a byproduct of the process, False otherwise.",
    )


class ElementaryFlowCompartment(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="elementary_flow_compartments",
    )

    name = models.CharField(
        max_length=128,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    parent_compartment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sub_compartments",
        help_text="Parent compartment if this is a sub-compartment.",
    )

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class ElementaryFlow(models.Model):

    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        related_name="elementary_flows",
    )

    compartment = models.ForeignKey(
        ElementaryFlowCompartment,
        on_delete=models.CASCADE,
        related_name="elementary_flows",
    )

    conserved_entity = models.ForeignKey(
        ConservedEntity,
        on_delete=models.CASCADE,
        related_name="elementary_flows",
    )

    quantity = models.FloatField(
        help_text="Quantity of conserved entity in the elementary flow.",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        help_text="Unit of the quantity.",
    )

    direction = models.CharField(
        max_length=10,
        choices=[("input", "Input"), ("output", "Output")],
        help_text="Indicates whether the conserved entity is an input to or an output from the process.",
    )
