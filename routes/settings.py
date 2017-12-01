from flask import Blueprint, request
from contentful.errors import HTTPError

from routes.base import locale, \
                        api_id, \
                        contentful, \
                        update_session_for, \
                        render_with_globals, \
                        VIEWS_PATH
from routes.errors import wrap_errors
from i18n.i18n import translate
from services.contentful import Contentful


settings = Blueprint('settings', __name__, template_folder=VIEWS_PATH)


@settings.route('/settings')
@wrap_errors
def show_settings():
    space = contentful().space(api_id())

    return render_with_globals(
        'settings',
        title=translate('settingsLabel', locale().code),
        errors={},
        has_errors=False,
        success=False,
        space=space
    )


@settings.route('/settings', methods=['POST'])
@wrap_errors
def save_settings():
    errors = {}
    space_id = request.values.get('spaceId', None)
    delivery_token = request.values.get('deliveryToken', None)
    preview_token = request.values.get('previewToken', None)
    editorial_features = bool(request.values.get('editorialFeatures', False))

    check_field_required(errors, space_id, 'spaceId')
    check_field_required(errors, delivery_token, 'deliveryToken')
    check_field_required(errors, preview_token, 'previewToken')

    if not errors:
        validate_space_token_combination(errors, space_id, delivery_token)
        validate_space_token_combination(errors, space_id, preview_token, True)

    if not errors:
        update_session_for('space_id', space_id)
        update_session_for('delivery_token', delivery_token)
        update_session_for('preview_token', preview_token)
        update_session_for('editorial_features', editorial_features)

    space = contentful().space(api_id())

    return render_with_globals(
        'settings',
        title=translate('settingsLabel', locale().code),
        errors=errors,
        has_errors=bool(errors),
        success=not bool(errors),
        space=space
    ), 201 if not errors else 409


def check_field_required(errors, element, field_name):
    if not element:
        append_error_message(
            errors,
            field_name,
            translate('fieldIsRequiredLabel', locale().code)
        )


def append_error_message(errors, field_name, message):
    if field_name not in errors:
        errors[field_name] = []
    if message not in errors[field_name]:
        errors[field_name].append(message)


def validate_space_token_combination(
        errors, space_id, access_token, is_preview=False):
    try:
        Contentful.create_client(space_id, access_token, is_preview)
    except HTTPError as e:
        token_field = 'previewToken' if is_preview else 'deliveryToken'

        if e.status_code == 401:
            error_label = 'deliveryKeyInvalidLabel'
            if is_preview:
                error_label = 'previewKeyInvalidLabel'

            append_error_message(
                errors,
                token_field,
                translate(error_label, locale().code)
            )
        elif e.status_code == 404:
            append_error_message(
                errors,
                'space_id',
                translate('spaceOrTokenInvalid', locale().code)
            )
        else:
            append_error_message(
                errors,
                token_field,
                translate('somethingWentWrongLabel', locale().code)
            )