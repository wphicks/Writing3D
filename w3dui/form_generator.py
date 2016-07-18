import pyw3d
import wtforms
import logging


class W3DToWTValidator(object):
    """A WT validator createdfrom a W3D Validator"""

    def __call__(self, form, field):
        if not self.w3d_validator(field.data):
            raise wtforms.validators.ValidationError(
                message=self.w3d_validator.help()
            )

    def __init__(self, w3d_validator):
        self.w3d_validator = w3d_validator


def field_from_validator(w3d_validator, label, required=False):
    """Generate field for a WTForm from a W3D Validator"""
    # TODO: Add coercion to process_data methods of fields
    validator_list = [W3DToWTValidator(w3d_validator)]
    kwargs = {}
    if required:
        validator_list.append(wtforms.validators.InputRequired())

    if isinstance(w3d_validator, pyw3d.validators.TextValidator):
        field_type = wtforms.fields.TextField

    elif isinstance(w3d_validator, pyw3d.validators.ValidPyString):
        field_type = wtforms.fields.TextField

    elif isinstance(w3d_validator, pyw3d.validators.ValidFile):
        field_type = wtforms.fields.FileField

    elif isinstance(w3d_validator, pyw3d.validators.IsBoolean):
        field_type = wtforms.fields.RadioField
        kwargs["coerce"] = w3d_validator.coerce

    elif isinstance(w3d_validator, pyw3d.validators.OptionValidator):
        field_type = wtforms.fields.SelectField
        kwargs["coerce"] = w3d_validator.coerce
        kwargs["choices"] = w3d_validator.valid_menu_items
        # TODO: The above needs to be determined dynamically
        # TODO: ReferenceValidator

    elif isinstance(w3d_validator, pyw3d.validators.ListValidator):
        # TODO: SortedListValidator
        if w3d_validator.required_length is not None:
            form_name = "{}Form".format(w3d_validator.__class__.__name__)
            form_fields = {
                "entry{}".format(i): field_from_validator(
                    w3d_validator.get_base_validator(i),
                    "{}".format(i)
                ) for i in range(w3d_validator.required_length)
            }
            return wtforms.fields.FormField(
                type(form_name, (wtforms.Form,), form_fields),
                label  # , validator_list
            )
        return wtforms.fields.FieldList(
            field_from_validator(
                w3d_validator.get_base_validator(0),
                "Entry"
            ),
            label, validator_list
        )

    elif isinstance(w3d_validator, pyw3d.validators.DictValidator):
        form_name = "{}Form".format(w3d_validator.__class__.__name__)
        form_fields = {
            "key": field_from_validator(w3d_validator.key_validator, "key"),
            "value": field_from_validator(
                w3d_validator.value_validator, "value")
        }
        return wtforms.fields.FormField(
            type(form_name, (wtforms.Form,), form_fields),
            label  # , validator_list
        )

    elif isinstance(w3d_validator, pyw3d.validators.IsInteger):
        field_type = wtforms.fields.IntegerField

    elif isinstance(w3d_validator, pyw3d.validators.IsNumeric):
        field_type = wtforms.fields.DecimalField
        kwargs["places"] = 4

    elif isinstance(w3d_validator, pyw3d.validators.FeatureValidator):
        return wtforms.fields.FormField(
            generate_form_class(w3d_validator.correct_class),
            label  # , validator_list
        )

    elif isinstance(w3d_validator, pyw3d.validators.Validator):
        field_type = wtforms.fields.Field

    return field_type(label, validator_list, **kwargs)


def generate_form_class(feature):
    """Generate WTForm class for editing W3DFeature

    :param W3DFeature feature: The feature to be edited or a W3DFeature
    subclass"""

    if type(feature) is type:
        class_name = "{}Form".format(feature.__name__)
    else:
        class_name = "{}Form".format(feature.__class__.__name__)

    class_attributes = {}
    for attribute, validator in feature.argument_validators.items():
        logging.debug(
            "Creating attribute {} in form {}".format(attribute, class_name)
        )
        class_attributes[attribute] = field_from_validator(
            validator,
            attribute,
            required=(attribute not in feature.default_arguments.keys())
        )

    return type(class_name, (wtforms.Form,), class_attributes)


class W3D_Form(wtforms.Form):
    """A WTForm for editing a W3DFeature

    :param W3DFeature feature: The feature to be edited
    """

    def __init__(self, feature):
        self.feature = feature
