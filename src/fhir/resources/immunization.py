# -*- coding: utf-8 -*-
"""
Profile: http://hl7.org/fhir/StructureDefinition/Immunization
Release: R4
Version: 4.5.0
Build ID: 0d95498
Last updated: 2021-04-03T00:34:11.075+00:00
"""
import typing
from pydantic import Field
from pydantic import root_validator

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic.errors import MissingError, NoneIsNotAllowedError

from . import fhirtypes


from . import domainresource


class Immunization(domainresource.DomainResource):
    """Disclaimer: Any field name ends with ``__ext`` doesn't part of
    Resource StructureDefinition, instead used to enable Extensibility feature
    for FHIR Primitive Data Types.

    Immunization event information.
    Describes the event of a patient being administered a vaccine or a record
    of an immunization as reported by a patient, a clinician or another party.
    """

    resource_type = Field("Immunization", const=True)

    basedOn: typing.List[fhirtypes.ReferenceType] = Field(
        None,
        alias="basedOn",
        title="Authority that the immunization event is based on",
        description=(
            "A plan, order or recommendation fulfilled in whole or in part by this "
            "immunization."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=[
            "CarePlan",
            "MedicationRequest",
            "ImmunizationRecommendation",
        ],
    )

    doseQuantity: fhirtypes.QuantityType = Field(
        None,
        alias="doseQuantity",
        title="Amount of vaccine administered",
        description="The quantity of vaccine product that was administered.",
        # if property is element of this resource.
        element_property=True,
    )

    education: typing.List[fhirtypes.ImmunizationEducationType] = Field(
        None,
        alias="education",
        title="Educational material presented to patient",
        description=(
            "Educational material presented to the patient (or guardian) at the "
            "time of vaccine administration."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    encounter: fhirtypes.ReferenceType = Field(
        None,
        alias="encounter",
        title="Encounter immunization was part of",
        description=(
            "The visit or admission or other contact between patient and health "
            "care provider the immunization was performed as part of."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Encounter"],
    )

    expirationDate: fhirtypes.Date = Field(
        None,
        alias="expirationDate",
        title="Vaccine expiration date",
        description="Date vaccine batch expires.",
        # if property is element of this resource.
        element_property=True,
    )
    expirationDate__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_expirationDate", title="Extension field for ``expirationDate``."
    )

    fundingSource: fhirtypes.CodeableConceptType = Field(
        None,
        alias="fundingSource",
        title="Funding source for the vaccine",
        description=(
            "Indicates the source of the vaccine actually administered. This may be"
            " different than the patient eligibility (e.g. the patient may be "
            "eligible for a publically purchased vaccine but due to inventory "
            "issues, vaccine purchased with private funds was actually "
            "administered)."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    identifier: typing.List[fhirtypes.IdentifierType] = Field(
        None,
        alias="identifier",
        title="Business identifier",
        description="A unique identifier assigned to this immunization record.",
        # if property is element of this resource.
        element_property=True,
    )

    informationSourceCodeableConcept: fhirtypes.CodeableConceptType = Field(
        None,
        alias="informationSourceCodeableConcept",
        title="Indicates the source of a  reported record",
        description=(
            "Typically the source of the data when the report of the immunization "
            "event is not based on information from the person who administered the"
            " vaccine."
        ),
        # if property is element of this resource.
        element_property=True,
        # Choice of Data Types. i.e informationSource[x]
        one_of_many="informationSource",
        one_of_many_required=False,
    )

    informationSourceReference: fhirtypes.ReferenceType = Field(
        None,
        alias="informationSourceReference",
        title="Indicates the source of a  reported record",
        description=(
            "Typically the source of the data when the report of the immunization "
            "event is not based on information from the person who administered the"
            " vaccine."
        ),
        # if property is element of this resource.
        element_property=True,
        # Choice of Data Types. i.e informationSource[x]
        one_of_many="informationSource",
        one_of_many_required=False,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=[
            "Patient",
            "Practitioner",
            "PractitionerRole",
            "RelatedPerson",
            "Organization",
        ],
    )

    instantiatesCanonical: typing.List[fhirtypes.Canonical] = Field(
        None,
        alias="instantiatesCanonical",
        title="Instantiates FHIR protocol or definition for the immunization event",
        description=(
            "The URL pointing to a FHIR-defined protocol, guideline, orderset or "
            "other definition that is adhered to in whole or in part by this "
            "Immunization."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=[
            "ActivityDefinition",
            "EventDefinition",
            "EvidenceVariable",
            "Measure",
            "OperationDefinition",
            "PlanDefinition",
            "Questionnaire",
            "SubscriptionTopic",
        ],
    )
    instantiatesCanonical__ext: typing.List[
        typing.Union[fhirtypes.FHIRPrimitiveExtensionType, None]
    ] = Field(
        None,
        alias="_instantiatesCanonical",
        title="Extension field for ``instantiatesCanonical``.",
    )

    instantiatesUri: typing.List[fhirtypes.Uri] = Field(
        None,
        alias="instantiatesUri",
        title=(
            "Instantiates external protocol or definition for the immunization " "event"
        ),
        description=(
            "The URL pointing to an externally maintained protocol, guideline, "
            "orderset or other definition that is adhered to in whole or in part by"
            " this Immunization."
        ),
        # if property is element of this resource.
        element_property=True,
    )
    instantiatesUri__ext: typing.List[
        typing.Union[fhirtypes.FHIRPrimitiveExtensionType, None]
    ] = Field(
        None, alias="_instantiatesUri", title="Extension field for ``instantiatesUri``."
    )

    isSubpotent: bool = Field(
        None,
        alias="isSubpotent",
        title="Dose potency",
        description=(
            "Indication if a dose is considered to be subpotent. By default, a dose"
            " should be considered to be potent."
        ),
        # if property is element of this resource.
        element_property=True,
    )
    isSubpotent__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_isSubpotent", title="Extension field for ``isSubpotent``."
    )

    location: fhirtypes.ReferenceType = Field(
        None,
        alias="location",
        title="Where immunization occurred",
        description=(
            "The service delivery location where the vaccine administration "
            "occurred."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Location"],
    )

    lotNumber: fhirtypes.String = Field(
        None,
        alias="lotNumber",
        title="Vaccine lot number",
        description="Lot number of the  vaccine product.",
        # if property is element of this resource.
        element_property=True,
    )
    lotNumber__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_lotNumber", title="Extension field for ``lotNumber``."
    )

    manufacturer: fhirtypes.ReferenceType = Field(
        None,
        alias="manufacturer",
        title="Vaccine manufacturer",
        description="Name of vaccine manufacturer.",
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Organization"],
    )

    note: typing.List[fhirtypes.AnnotationType] = Field(
        None,
        alias="note",
        title="Additional immunization notes",
        description=(
            "Extra information about the immunization that is not conveyed by the "
            "other attributes."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    occurrenceDateTime: fhirtypes.DateTime = Field(
        None,
        alias="occurrenceDateTime",
        title="Vaccine administration date",
        description="Date vaccine administered or was to be administered.",
        # if property is element of this resource.
        element_property=True,
        # Choice of Data Types. i.e occurrence[x]
        one_of_many="occurrence",
        one_of_many_required=True,
    )
    occurrenceDateTime__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None,
        alias="_occurrenceDateTime",
        title="Extension field for ``occurrenceDateTime``.",
    )

    occurrenceString: fhirtypes.String = Field(
        None,
        alias="occurrenceString",
        title="Vaccine administration date",
        description="Date vaccine administered or was to be administered.",
        # if property is element of this resource.
        element_property=True,
        # Choice of Data Types. i.e occurrence[x]
        one_of_many="occurrence",
        one_of_many_required=True,
    )
    occurrenceString__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None,
        alias="_occurrenceString",
        title="Extension field for ``occurrenceString``.",
    )

    patient: fhirtypes.ReferenceType = Field(
        ...,
        alias="patient",
        title="Who was immunized",
        description="The patient who either received or did not receive the immunization.",
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Patient"],
    )

    performer: typing.List[fhirtypes.ImmunizationPerformerType] = Field(
        None,
        alias="performer",
        title="Who performed event",
        description="Indicates who performed the immunization event.",
        # if property is element of this resource.
        element_property=True,
    )

    primarySource: bool = Field(
        None,
        alias="primarySource",
        title="Indicates context the data was recorded in",
        description=(
            "Indicates if this record was captured as a secondary 'reported' record"
            " rather than as an original primary source-of-truth record."
        ),
        # if property is element of this resource.
        element_property=True,
    )
    primarySource__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_primarySource", title="Extension field for ``primarySource``."
    )

    programEligibility: typing.List[fhirtypes.CodeableConceptType] = Field(
        None,
        alias="programEligibility",
        title="Patient eligibility for a vaccination program",
        description="Indicates a patient's eligibility for a funding program.",
        # if property is element of this resource.
        element_property=True,
    )

    protocolApplied: typing.List[fhirtypes.ImmunizationProtocolAppliedType] = Field(
        None,
        alias="protocolApplied",
        title="Protocol followed by the provider",
        description=(
            "The protocol (set of recommendations) being followed by the provider "
            "who administered the dose."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    reaction: typing.List[fhirtypes.ImmunizationReactionType] = Field(
        None,
        alias="reaction",
        title="Details of a reaction that follows immunization",
        description=(
            "Categorical data indicating that an adverse event is associated in "
            "time to an immunization."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    reason: typing.List[fhirtypes.CodeableReferenceType] = Field(
        None,
        alias="reason",
        title="Why immunization occurred",
        description=(
            "Describes why the immunization occurred in coded or textual form, or "
            "Indicates another resource (Condition, Observation or "
            "DiagnosticReport) whose existence justifies this immunization."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Condition", "Observation", "DiagnosticReport"],
    )

    recorded: fhirtypes.DateTime = Field(
        None,
        alias="recorded",
        title="When the immunization was first captured in the subject's record",
        description=(
            "The date the occurrence of the immunization was first captured in the "
            "record - potentially significantly after the occurrence of the event."
        ),
        # if property is element of this resource.
        element_property=True,
    )
    recorded__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_recorded", title="Extension field for ``recorded``."
    )

    route: fhirtypes.CodeableConceptType = Field(
        None,
        alias="route",
        title="How vaccine entered body",
        description="The path by which the vaccine product is taken into the body.",
        # if property is element of this resource.
        element_property=True,
    )

    site: fhirtypes.CodeableConceptType = Field(
        None,
        alias="site",
        title="Body site vaccine  was administered",
        description="Body site where vaccine was administered.",
        # if property is element of this resource.
        element_property=True,
    )

    status: fhirtypes.Code = Field(
        None,
        alias="status",
        title="completed | entered-in-error | not-done",
        description="Indicates the current status of the immunization event.",
        # if property is element of this resource.
        element_property=True,
        element_required=True,
        # note: Enum values can be used in validation,
        # but use in your own responsibilities, read official FHIR documentation.
        enum_values=["completed", "entered-in-error", "not-done"],
    )
    status__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_status", title="Extension field for ``status``."
    )

    statusReason: fhirtypes.CodeableConceptType = Field(
        None,
        alias="statusReason",
        title="Reason for current status",
        description="Indicates the reason the immunization event was not performed.",
        # if property is element of this resource.
        element_property=True,
    )

    subpotentReason: typing.List[fhirtypes.CodeableConceptType] = Field(
        None,
        alias="subpotentReason",
        title="Reason for being subpotent",
        description="Reason why a dose is considered to be subpotent.",
        # if property is element of this resource.
        element_property=True,
    )

    vaccineCode: fhirtypes.CodeableConceptType = Field(
        ...,
        alias="vaccineCode",
        title="Vaccine product administered",
        description="Vaccine that was administered or was to be administered.",
        # if property is element of this resource.
        element_property=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from ``Immunization`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "meta",
            "implicitRules",
            "language",
            "text",
            "contained",
            "extension",
            "modifierExtension",
            "identifier",
            "instantiatesCanonical",
            "instantiatesUri",
            "basedOn",
            "status",
            "statusReason",
            "vaccineCode",
            "manufacturer",
            "lotNumber",
            "expirationDate",
            "patient",
            "encounter",
            "occurrenceDateTime",
            "occurrenceString",
            "recorded",
            "primarySource",
            "informationSourceCodeableConcept",
            "informationSourceReference",
            "location",
            "site",
            "route",
            "doseQuantity",
            "performer",
            "note",
            "reason",
            "isSubpotent",
            "subpotentReason",
            "education",
            "programEligibility",
            "fundingSource",
            "reaction",
            "protocolApplied",
        ]

    @root_validator(pre=True, allow_reuse=True)
    def validate_required_primitive_elements_1467(
        cls, values: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """https://www.hl7.org/fhir/extensibility.html#Special-Case
        In some cases, implementers might find that they do not have appropriate data for
        an element with minimum cardinality = 1. In this case, the element must be present,
        but unless the resource or a profile on it has made the actual value of the primitive
        data type mandatory, it is possible to provide an extension that explains why
        the primitive value is not present.
        """
        required_fields = [("status", "status__ext")]
        _missing = object()

        def _fallback():
            return ""

        errors: typing.List["ErrorWrapper"] = []
        for name, ext in required_fields:
            field = cls.__fields__[name]
            ext_field = cls.__fields__[ext]
            value = values.get(field.alias, _missing)
            if value not in (_missing, None):
                continue
            ext_value = values.get(ext_field.alias, _missing)
            missing_ext = True
            if ext_value not in (_missing, None):
                if isinstance(ext_value, dict):
                    missing_ext = len(ext_value.get("extension", [])) == 0
                elif (
                    getattr(ext_value.__class__, "get_resource_type", _fallback)()
                    == "FHIRPrimitiveExtension"
                ):
                    if ext_value.extension and len(ext_value.extension) > 0:
                        missing_ext = False
                else:
                    validate_pass = True
                    for validator in ext_field.type_.__get_validators__():
                        try:
                            ext_value = validator(v=ext_value)
                        except ValidationError as exc:
                            errors.append(ErrorWrapper(exc, loc=ext_field.alias))
                            validate_pass = False
                    if not validate_pass:
                        continue
                    if ext_value.extension and len(ext_value.extension) > 0:
                        missing_ext = False
            if missing_ext:
                if value is _missing:
                    errors.append(ErrorWrapper(MissingError(), loc=field.alias))
                else:
                    errors.append(
                        ErrorWrapper(NoneIsNotAllowedError(), loc=field.alias)
                    )
        if len(errors) > 0:
            raise ValidationError(errors, cls)  # type: ignore

        return values

    @root_validator(pre=True, allow_reuse=True)
    def validate_one_of_many_1467(
        cls, values: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """https://www.hl7.org/fhir/formats.html#choice
        A few elements have a choice of more than one data type for their content.
        All such elements have a name that takes the form nnn[x].
        The "nnn" part of the name is constant, and the "[x]" is replaced with
        the title-cased name of the type that is actually used.
        The table view shows each of these names explicitly.

        Elements that have a choice of data type cannot repeat - they must have a
        maximum cardinality of 1. When constructing an instance of an element with a
        choice of types, the authoring system must create a single element with a
        data type chosen from among the list of permitted data types.
        """
        one_of_many_fields = {
            "informationSource": [
                "informationSourceCodeableConcept",
                "informationSourceReference",
            ],
            "occurrence": ["occurrenceDateTime", "occurrenceString"],
        }
        for prefix, fields in one_of_many_fields.items():
            assert cls.__fields__[fields[0]].field_info.extra["one_of_many"] == prefix
            required = (
                cls.__fields__[fields[0]].field_info.extra["one_of_many_required"]
                is True
            )
            found = False
            for field in fields:
                if field in values and values[field] is not None:
                    if found is True:
                        raise ValueError(
                            "Any of one field value is expected from "
                            f"this list {fields}, but got multiple!"
                        )
                    else:
                        found = True
            if required is True and found is False:
                raise ValueError(f"Expect any of field value from this list {fields}.")

        return values


from . import backboneelement


class ImmunizationEducation(backboneelement.BackboneElement):
    """Disclaimer: Any field name ends with ``__ext`` doesn't part of
    Resource StructureDefinition, instead used to enable Extensibility feature
    for FHIR Primitive Data Types.

    Educational material presented to patient.
    Educational material presented to the patient (or guardian) at the time of
    vaccine administration.
    """

    resource_type = Field("ImmunizationEducation", const=True)

    documentType: fhirtypes.String = Field(
        None,
        alias="documentType",
        title="Educational material document identifier",
        description="Identifier of the material presented to the patient.",
        # if property is element of this resource.
        element_property=True,
    )
    documentType__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_documentType", title="Extension field for ``documentType``."
    )

    presentationDate: fhirtypes.DateTime = Field(
        None,
        alias="presentationDate",
        title="Educational material presentation date",
        description="Date the educational material was given to the patient.",
        # if property is element of this resource.
        element_property=True,
    )
    presentationDate__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None,
        alias="_presentationDate",
        title="Extension field for ``presentationDate``.",
    )

    publicationDate: fhirtypes.DateTime = Field(
        None,
        alias="publicationDate",
        title="Educational material publication date",
        description="Date the educational material was published.",
        # if property is element of this resource.
        element_property=True,
    )
    publicationDate__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_publicationDate", title="Extension field for ``publicationDate``."
    )

    reference: fhirtypes.Uri = Field(
        None,
        alias="reference",
        title="Educational material reference pointer",
        description=(
            "Reference pointer to the educational material given to the patient if "
            "the information was on line."
        ),
        # if property is element of this resource.
        element_property=True,
    )
    reference__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_reference", title="Extension field for ``reference``."
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from ``ImmunizationEducation`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "modifierExtension",
            "documentType",
            "reference",
            "publicationDate",
            "presentationDate",
        ]


class ImmunizationPerformer(backboneelement.BackboneElement):
    """Disclaimer: Any field name ends with ``__ext`` doesn't part of
    Resource StructureDefinition, instead used to enable Extensibility feature
    for FHIR Primitive Data Types.

    Who performed event.
    Indicates who performed the immunization event.
    """

    resource_type = Field("ImmunizationPerformer", const=True)

    actor: fhirtypes.ReferenceType = Field(
        ...,
        alias="actor",
        title="Individual or organization who was performing",
        description="The practitioner or organization who performed the action.",
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Practitioner", "PractitionerRole", "Organization"],
    )

    function: fhirtypes.CodeableConceptType = Field(
        None,
        alias="function",
        title="What type of performance was done",
        description=(
            "Describes the type of performance (e.g. ordering provider, "
            "administering provider, etc.)."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from ``ImmunizationPerformer`` according specification,
        with preserving original sequence order.
        """
        return ["id", "extension", "modifierExtension", "function", "actor"]


class ImmunizationProtocolApplied(backboneelement.BackboneElement):
    """Disclaimer: Any field name ends with ``__ext`` doesn't part of
    Resource StructureDefinition, instead used to enable Extensibility feature
    for FHIR Primitive Data Types.

    Protocol followed by the provider.
    The protocol (set of recommendations) being followed by the provider who
    administered the dose.
    """

    resource_type = Field("ImmunizationProtocolApplied", const=True)

    authority: fhirtypes.ReferenceType = Field(
        None,
        alias="authority",
        title="Who is responsible for publishing the recommendations",
        description=(
            "Indicates the authority who published the protocol (e.g. ACIP) that is"
            " being followed."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Organization"],
    )

    doseNumber: fhirtypes.String = Field(
        None,
        alias="doseNumber",
        title="Dose number within series",
        description=(
            "Nominal position in a series as intended by the practitioner "
            "administering the dose."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )
    doseNumber__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_doseNumber", title="Extension field for ``doseNumber``."
    )

    series: fhirtypes.String = Field(
        None,
        alias="series",
        title="Name of vaccine series",
        description=(
            "One possible path to achieve presumed immunity against a disease - "
            "within the context of an authority."
        ),
        # if property is element of this resource.
        element_property=True,
    )
    series__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_series", title="Extension field for ``series``."
    )

    seriesDoses: fhirtypes.String = Field(
        None,
        alias="seriesDoses",
        title="Recommended number of doses for immunity",
        description=(
            "The recommended number of doses to achieve immunity as intended by the"
            " practitioner administering the dose."
        ),
        # if property is element of this resource.
        element_property=True,
    )
    seriesDoses__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_seriesDoses", title="Extension field for ``seriesDoses``."
    )

    targetDisease: typing.List[fhirtypes.CodeableConceptType] = Field(
        None,
        alias="targetDisease",
        title="Vaccine preventatable disease being targetted",
        description=(
            "The vaccine preventable disease the dose is being administered " "against."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from ``ImmunizationProtocolApplied`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "modifierExtension",
            "series",
            "authority",
            "targetDisease",
            "doseNumber",
            "seriesDoses",
        ]

    @root_validator(pre=True, allow_reuse=True)
    def validate_required_primitive_elements_3010(
        cls, values: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """https://www.hl7.org/fhir/extensibility.html#Special-Case
        In some cases, implementers might find that they do not have appropriate data for
        an element with minimum cardinality = 1. In this case, the element must be present,
        but unless the resource or a profile on it has made the actual value of the primitive
        data type mandatory, it is possible to provide an extension that explains why
        the primitive value is not present.
        """
        required_fields = [("doseNumber", "doseNumber__ext")]
        _missing = object()

        def _fallback():
            return ""

        errors: typing.List["ErrorWrapper"] = []
        for name, ext in required_fields:
            field = cls.__fields__[name]
            ext_field = cls.__fields__[ext]
            value = values.get(field.alias, _missing)
            if value not in (_missing, None):
                continue
            ext_value = values.get(ext_field.alias, _missing)
            missing_ext = True
            if ext_value not in (_missing, None):
                if isinstance(ext_value, dict):
                    missing_ext = len(ext_value.get("extension", [])) == 0
                elif (
                    getattr(ext_value.__class__, "get_resource_type", _fallback)()
                    == "FHIRPrimitiveExtension"
                ):
                    if ext_value.extension and len(ext_value.extension) > 0:
                        missing_ext = False
                else:
                    validate_pass = True
                    for validator in ext_field.type_.__get_validators__():
                        try:
                            ext_value = validator(v=ext_value)
                        except ValidationError as exc:
                            errors.append(ErrorWrapper(exc, loc=ext_field.alias))
                            validate_pass = False
                    if not validate_pass:
                        continue
                    if ext_value.extension and len(ext_value.extension) > 0:
                        missing_ext = False
            if missing_ext:
                if value is _missing:
                    errors.append(ErrorWrapper(MissingError(), loc=field.alias))
                else:
                    errors.append(
                        ErrorWrapper(NoneIsNotAllowedError(), loc=field.alias)
                    )
        if len(errors) > 0:
            raise ValidationError(errors, cls)  # type: ignore

        return values


class ImmunizationReaction(backboneelement.BackboneElement):
    """Disclaimer: Any field name ends with ``__ext`` doesn't part of
    Resource StructureDefinition, instead used to enable Extensibility feature
    for FHIR Primitive Data Types.

    Details of a reaction that follows immunization.
    Categorical data indicating that an adverse event is associated in time to
    an immunization.
    """

    resource_type = Field("ImmunizationReaction", const=True)

    date: fhirtypes.DateTime = Field(
        None,
        alias="date",
        title="When reaction started",
        description="Date of reaction to the immunization.",
        # if property is element of this resource.
        element_property=True,
    )
    date__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_date", title="Extension field for ``date``."
    )

    detail: fhirtypes.ReferenceType = Field(
        None,
        alias="detail",
        title="Additional information on reaction",
        description="Details of the reaction.",
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Observation"],
    )

    reported: bool = Field(
        None,
        alias="reported",
        title="Indicates self-reported reaction",
        description="Self-reported indicator.",
        # if property is element of this resource.
        element_property=True,
    )
    reported__ext: fhirtypes.FHIRPrimitiveExtensionType = Field(
        None, alias="_reported", title="Extension field for ``reported``."
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from ``ImmunizationReaction`` according specification,
        with preserving original sequence order.
        """
        return ["id", "extension", "modifierExtension", "date", "detail", "reported"]
