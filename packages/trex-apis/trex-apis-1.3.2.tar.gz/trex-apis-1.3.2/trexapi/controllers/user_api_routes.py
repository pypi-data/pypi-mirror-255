'''
Created on 7 Jul 2021

@author: jacklok
'''

from flask import Blueprint, request
import logging
from trexlib.utils.log_util import get_tracelog
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime, timedelta
from trexlib.utils.string_util import is_not_empty, random_number, random_string,\
    is_empty
from trexmodel.models.datastore.user_models import User
from trexadmin.libs.http import create_rest_message
from trexadmin.libs.http import StatusCode
from werkzeug.datastructures import ImmutableMultiDict
from trexapi.forms.user_api_forms import UserRegistrationForm, UserUpdateForm,\
    OutletReviewsForm
from trexapi.conf import APPLICATION_NAME, APPLICATION_BASE_URL, MOBILE_APP_NAME
from trexmail.email_helper import trigger_send_email
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher,\
    CustomerPointReward, CustomerEntitledTierRewardSummary
from trexapi.utils.api_helpers import generate_user_auth_token
from trexapi.decorators.api_decorators import user_auth_token_required
from trexadmin.libs.decorators import elapsed_time_trace
from flask.json import jsonify
from trexlib.conf import PRODUCTION_MODE, DEPLOYMENT_MODE, DEMO_MODE, LOCAL_MODE
from flask_babel import gettext
#from trexadmin import conf
from trexmodel import conf as model_conf
import os
from trexlib.utils.sms_util import send_sms
from trexmodel.models.datastore.message_models import Message
from time import strftime
from trexlib.utils.common.date_util import from_utc_datetime_to_local_datetime
from trexmodel.conf import USER_STATUS_REGISTERED, GENDER_UNKNOWN_CODE
from trexmodel.models.datastore.model_decorators import model_transactional

user_api_bp = Blueprint('user_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/users')

logger = logging.getLogger('api')


@user_api_bp.route('/guest-register', methods=['POST'])
def guest_register():
    logger.debug('---guest_register---')
    
    try:
        user_data_in_json   = request.get_json()
        logger.debug('guest_register: user_data_in_json=%s', user_data_in_json)
        
        register_user_form  = UserRegistrationForm(ImmutableMultiDict(user_data_in_json))
        if register_user_form.validate():
            logger.debug('guest_register:  registration input is valid')
            db_client = create_db_client(caller_info="guest_register")
            
            registered_user_acct    = None
            
            with db_client.context():
                name            = register_user_form.name.data
                
                logger.debug('name=%s', name)
                
                registered_user_acct = User.create(name=name)
                        
                
                                
            if registered_user_acct is not None:
                
                (expiry_datetime, token)    = generate_user_auth_token(registered_user_acct.user_id, registered_user_acct.reference_code)
                
                return create_rest_message(status_code=StatusCode.OK, 
                                           auth_token                           = token,
                                           reference_code                       = registered_user_acct.reference_code,
                                           )
            else:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = register_user_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('user_register: Fail to register user due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/register', methods=['POST'])
def user_register():
    logger.debug('user_register: ---user_register---')
    
    try:
        user_data_in_json   = request.get_json()
        logger.debug('user_register: user_data_in_json=%s', user_data_in_json)
        
        register_user_form  = UserRegistrationForm(ImmutableMultiDict(user_data_in_json))
        if register_user_form.validate():
            logger.debug('user_register:  registration input is valid')
            db_client = create_db_client(caller_info="user_register")
            
            registered_user_acct    = None
            
            with db_client.context():
                email           = register_user_form.email.data
                name            = register_user_form.name.data
                mobile_phone    = register_user_form.mobile_phone.data
                birth_date      = register_user_form.birth_date.data
                gender          = register_user_form.gender.data
                password        = register_user_form.password.data
                status          = register_user_form.status.data
                
                if is_not_empty(birth_date):
                    birth_date = datetime.strptime(birth_date, '%d-%m-%Y')
                else:
                    birth_date = None
                    
                if is_empty(gender):
                    gender = model_conf.GENDER_UNKNOWN_CODE
                
                logger.debug('email=%s', email)
                logger.debug('name=%s', name)
                logger.debug('mobile_phone=%s', mobile_phone)
                logger.debug('birth_date=%s', birth_date)
                logger.debug('gender=%s', gender)
                logger.debug('password=%s', password)
                logger.debug('status=%s', status)
                
                checking_registered_user_acct = User.get_by_email(email)
                if checking_registered_user_acct is None:
                    if is_not_empty(mobile_phone):
                        checking_registered_user_acct = User.get_by_mobile_phone(mobile_phone)
                        if checking_registered_user_acct is None:
                            registered_user_acct = User.create(
                                                                name                        = name, 
                                                                email                       = email, 
                                                                mobile_phone                = mobile_phone, 
                                                                birth_date                  = birth_date,
                                                                gender                      = gender,
                                                                password                    = password, 
                                                                is_email_verified           = True, 
                                                                is_mobile_phone_verified    = True,
                                                                status                      = USER_STATUS_REGISTERED,
                                                               )
                            logger.debug('new registered_user_acct=%s', registered_user_acct)
                        else:
                            if checking_registered_user_acct.is_mobile_phone_verified==True:
                                return create_rest_message('Mobile Phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    else:
                        registered_user_acct = User.create(
                                                                name                = name, 
                                                                email               = email, 
                                                                birth_date          = birth_date,
                                                                gender              = gender,
                                                                password            = password, 
                                                                is_email_verified   = True,
                                                                status              = USER_STATUS_REGISTERED,
                                                               )
                        
                        logger.debug('new registered_user_acct=%s', registered_user_acct)
                        
                else:
                    return create_rest_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                
                                
            if registered_user_acct is not None:
                
                (expiry_datetime, token)    = generate_user_auth_token(registered_user_acct.user_id, registered_user_acct.reference_code)
                
                return create_rest_message(status_code=StatusCode.OK, 
                                           auth_token                           = token,
                                           reference_code                       = registered_user_acct.reference_code,
                                           email_vc_expiry_datetime             = registered_user_acct.email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') if registered_user_acct.email_vc_expiry_datetime is not None else None,
                                           mobile_phone_vc_expiry_datetime      = registered_user_acct.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') if registered_user_acct.mobile_phone_vc_expiry_datetime is not None else None,
                                           status                               = registered_user_acct.status,
                                           )
            else:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = register_user_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('user_register: Fail to register user due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    

@user_api_bp.route('/update', methods=['POST'])
def user_update():
    logger.debug('user_update: ---user_register---')
    
    try:
        user_data_in_json   = request.get_json()
        logger.debug('user_update: user_data_in_json=%s', user_data_in_json)
        
        update_user_form  = UserUpdateForm(ImmutableMultiDict(user_data_in_json))
        if update_user_form.validate():
            logger.debug('update_user_form:  update input is valid')
            db_client = create_db_client(caller_info="user_update")
            
            with db_client.context():
                reference_code  = update_user_form.reference_code.data
                name            = update_user_form.name.data
                mobile_phone    = update_user_form.mobile_phone.data
                birth_date      = update_user_form.birth_date.data
                gender          = update_user_form.gender.data
                status          = update_user_form.status.data
                
                if is_not_empty(birth_date):
                    birth_date = datetime.strptime(birth_date, '%d-%m-%Y')
                else:
                    birth_date = None
                    
                if is_empty(gender):
                    gender = GENDER_UNKNOWN_CODE    
                
                
                logger.debug('reference_code=%s', reference_code)
                logger.debug('name=%s', name)
                logger.debug('mobile_phone=%s', mobile_phone)
                logger.debug('birth_date=%s', birth_date)
                logger.debug('gender=%s', gender)
                logger.debug('status=%s', status)
                
                user_acct = User.get_by_reference_code(reference_code)
                if user_acct:
                    original_mobile_phone   = user_acct.mobile_phone
                    
                    
                    if is_not_empty(mobile_phone):
                        logger.debug('going to update user details with mobile phone=%s', mobile_phone)
                        if original_mobile_phone!=mobile_phone:
                            logger.debug('mobile phone have been changed thus going to check whether new mobile phone is taken or not')
                            checking_mobile_phone_user_acct = User.get_by_mobile_phone(mobile_phone)
                            
                            if checking_mobile_phone_user_acct is None:
                                logger.debug('mobile phone is not taken')
                                
                                _update_user_acct(user_acct, 
                                            mobile_phone    = mobile_phone,
                                            name            = name,
                                            birth_date      = birth_date,
                                            gender          = gender,
                                            status          = status,
                                            ) 
                                
                            else:
                                return create_rest_message('Mobile Phone have been taken', status_code=StatusCode.BAD_REQUEST)
                        else:
                            logger.debug('mobile phone is not change')
                            
                            _update_user_acct(user_acct, 
                                            mobile_phone    = mobile_phone,
                                            name            = name,
                                            birth_date      = birth_date,
                                            gender          = gender,
                                            status          = status,
                                            ) 
                    
                    else:
                        logger.debug('going to update user details without mobile phone')
                        
                        _update_user_acct(user_acct, 
                                            mobile_phone    = mobile_phone,
                                            name            = name,
                                            birth_date      = birth_date,
                                            gender          = gender,
                                            status          = status,
                                            )         
                    
                else:
                    return create_rest_message('User account is not found', status_code=StatusCode.BAD_REQUEST)
                
                                
            return create_rest_message(status_code=StatusCode.OK)
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = update_user_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('user_register: Fail to update user due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@model_transactional(desc="_update_user_account")
def _update_user_acct(user_acct, mobile_phone=None, name=None, birth_date=None, gender=None, status=None):
    User.update(user_acct, 
                        mobile_phone    = mobile_phone,
                        name            = name,
                        birth_date      = birth_date,
                        gender          = gender,
                        status          = status,
                        )  
    Customer.update_all_from_user_acct(user_acct)  
    
    
@user_api_bp.route('/update-status', methods=['PUT'])
def user_update_status():
    logger.debug('---user_update_status---')
    
    reference_code      = request.headers.get('x-reference-code')
    
    try:
        user_data_in_json   = request.get_json()
        logger.debug('user_update_status: user_data_in_json=%s', user_data_in_json)
        
        update_user_status_form  = UserStatusForm(ImmutableMultiDict(user_data_in_json))
        if update_user_status_form.validate():
            logger.debug('update_user_status_form:  update input is valid')
            db_client = create_db_client(caller_info="user_update_status")
            
            with db_client.context():
                user = User.get_by_reference_code(reference_code)
                user.status = update_user_status_form.status.data
                user.put()
                
            return create_rest_message(status_code=StatusCode.ACCEPTED)

    except:
        logger.error('Fail to update user status due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        
@user_api_bp.route('/email-auth', methods=['POST'])
def auth_user_thru_email():
    
    user_data_in_json   = request.get_json()
    email               = user_data_in_json.get('email')
    password            = user_data_in_json.get('password')
    
    logger.debug('email=%s', email)
    logger.debug('password=%s', password)
    
    if is_not_empty(email) and is_not_empty(password):
        db_client = create_db_client(caller_info="auth_user")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            
            logger.debug('auth_user: found user account by email=%s', email)    
            logger.debug('auth_user: found user account by password=%s', password)
            
            if user_acct.is_still_lock:
                return create_rest_message('User account is locked after many trials for security purpose. Please try after an hour', status_code=StatusCode.BAD_REQUEST)
            else:
                if user_acct.deleted:
                    return create_rest_message('User email or password is invalid', status_code=StatusCode.BAD_REQUEST)
                else:
                    if user_acct.is_valid_password(password):
                    
                        (expiry_datetime, token)    = generate_user_auth_token(user_acct.user_id, user_acct.reference_code)
                        
                        response_data = {
                                            'auth_token'              : token,
                                            }
                            
                        response_data.update(user_details_dict(user_acct))
                        
                        logger.debug('auth_user debug: response_data=%s', response_data)
                        
                        return create_rest_message(status_code=StatusCode.OK, 
                                                   **response_data
                                                   
                                                   )
                    else:
                        
                        logger.warn('auth_user: user password is invalid')
                        with db_client.context():
                            user_acct.add_try_count()
                        
                        return create_rest_message('User email or password is not match', status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message('User email or password is not match', status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('auth_user: user verify input is invalid')
        return create_rest_message('Missing email or password', status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/mobile-phone-auth', methods=['POST'])
def auth_user_thru_mobile_phone():
    
    user_data_in_json   = request.get_json()
    mobile_phone        = user_data_in_json.get('mobile_phone')
    password            = user_data_in_json.get('password')
    
    logger.debug('mobile_phone=%s', mobile_phone)
    logger.debug('password=%s', password)
    
    if is_not_empty(mobile_phone) and is_not_empty(password):
        db_client = create_db_client(caller_info="auth_user")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_mobile_phone(mobile_phone)
        
        if user_acct:
            
            logger.debug('auth_user: found user account by mobile_phone=%s', mobile_phone)    
            logger.debug('auth_user: found user account by password=%s', password)
            
            if user_acct.is_still_lock:
                return create_rest_message('User account is locked after many trials for security purpose. Please try after an hour', status_code=StatusCode.BAD_REQUEST)
            else:
                if user_acct.deleted:
                    return create_rest_message('User mobile phone or password is invalid', status_code=StatusCode.BAD_REQUEST)
                else:
                    if user_acct.is_valid_password(password):
                    
                        (expiry_datetime, token)    = generate_user_auth_token(user_acct.user_id, user_acct.reference_code)
                        
                        response_data = {
                                            'auth_token'              : token,
                                            }
                            
                        response_data.update(user_details_dict(user_acct))
                        
                        logger.debug('auth_user debug: response_data=%s', response_data)
                        
                        return create_rest_message(status_code=StatusCode.OK, 
                                                   **response_data
                                                   
                                                   )
                    else:
                        
                        logger.warn('auth_user: user password is invalid')
                        with db_client.context():
                            user_acct.add_try_count()
                        
                        return create_rest_message('User mobile phone or password is not match', status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message('User mobile phone or password is not match', status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('auth_user: user verify input is invalid')
        return create_rest_message('Missing mobile phone or password', status_code=StatusCode.BAD_REQUEST)    



@user_api_bp.route('/set-email-verified', methods=['POST'])
@user_auth_token_required
def set_email_verified(reference_code):
    
    db_client = create_db_client(caller_info="set_email_verified")
    
    logger.debug('set_email_verified: going to find user account by reference code=%s', reference_code)
    
    with db_client.context():
        user_acct   = User.get_by_reference_code(reference_code)
    
    if user_acct:
        with db_client.context():
            user_acct.mark_email_verified()
        
        return create_rest_message(status_code=StatusCode.OK)
    
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/set-mobile-phone-verified', methods=['POST'])
@user_auth_token_required
def set_mobile_phone_verified(reference_code):
    
    db_client = create_db_client(caller_info="set_mobile_phone_verified")
    
    logger.debug('set_email_verified: going to find user account by reference code=%s', reference_code)
    
    with db_client.context():
        user_acct   = User.get_by_reference_code(reference_code)
    
    if user_acct:
        with db_client.context():
            user_acct.mark_mobile_phone_verified()
        
        return create_rest_message(status_code=StatusCode.OK)
    
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
            
      
@user_api_bp.route('/verify-email', methods=['POST'])
def verify_email_account():
    
    user_data_in_json   = request.get_json()
    email               = user_data_in_json.get('email')
    verification_code   = user_data_in_json.get('verification_code')
    
    
    if is_not_empty(email) and is_not_empty(verification_code):
        db_client = create_db_client(caller_info="verify_email_account")
        user_acct = None
        
        logger.debug('verify_email_account: going to find user account by email=%s', email)
        
        with db_client.context():
            user_acct   = User.get_by_email(email)
        
        if user_acct:
            logger.debug('verify_email_account: found user account by email=%s', email)    
            if user_acct.email_vc==verification_code:
                is_within_seconds = (user_acct.email_vc_expiry_datetime - datetime.now()).seconds
                if is_within_seconds>0:
                    with db_client.context():
                        user_acct.mark_email_verified()
                    return create_rest_message(status_code=StatusCode.OK)
                else:
                    return create_rest_message("Verification Code is expired already", status_code=StatusCode.BAD_REQUEST)
            
            else:
                logger.warn('verify_email_account: verification code is invalid')
                return create_rest_message("Invalid verification code", status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_email_account: user verify input is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
@user_api_bp.route('/verify-mobile-phone', methods=['POST'])
def verify_mobile_phone_account():
    
    user_data_in_json   = request.get_json()
    mobile_phone        = user_data_in_json.get('mobile_phone')
    verification_code   = user_data_in_json.get('verification_code')
    reference_code      = request.headers.get('x-reference-code')
    
    if is_not_empty(mobile_phone) and is_not_empty(verification_code):
        db_client = create_db_client(caller_info="verify_mobile_phone_account")
        user_acct = None
        with db_client.context():
            user_acct_by_mobile_phone   = User.get_by_mobile_phone(mobile_phone)
            user_acct                   = User.get_by_reference_code(reference_code)
        
        if user_acct_by_mobile_phone is None or user_acct_by_mobile_phone.reference_code == reference_code:
            if user_acct:
                logger.debug('verify_mobile_phone_account: found user account by mobile_phone=%s', mobile_phone)    
                if user_acct.mobile_phone_vc==verification_code:
                    is_within_seconds = (user_acct.mobile_phone_vc_expiry_datetime - datetime.now()).seconds
                    if is_within_seconds>0:
                        with db_client.context():
                            user_acct.mark_email_verified()
                        return create_rest_message(status_code=StatusCode.OK)
                    else:
                        return create_rest_message("Verification Code is expired already", status_code=StatusCode.BAD_REQUEST)
                
                else:
                    logger.warn('verify_mobile_phone_account: verification code is invalid')
                    return create_rest_message("Invalid verification code", status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                return create_rest_message(gettext('Invalid user account'), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext('Mobile phone have been taken'), status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_mobile_phone_account: user verify input is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)        

@user_api_bp.route('/register-as-customer', methods=['POST'])
#@user_auth_token_required
def register_user_as_customer():
    user_data_in_json           = request.get_json()
    reference_code              = user_data_in_json.get('reference_code')
    merchant_reference_code     = user_data_in_json.get('merchant_reference_code')
    outlet_key                  = user_data_in_json.get('outlet_key')
    
    logger.debug('register_user_as_customer: user_data_in_json=%s', user_data_in_json)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_user_as_customer")
            
            created_customer        = None
            existing_user_acct      = None
            is_email_used           = False
            is_mobile_phone_used    = False
            merchant_act_key        = None
            
            merchant_acct           = None
            
            with db_client.context():
                existing_user_acct  = User.get_by_reference_code(reference_code)
                if existing_user_acct:
                    outlet              = Outlet.fetch(outlet_key)
                        
                    if outlet:
                        merchant_acct       = outlet.merchant_acct_entity
                        merchant_act_key    = outlet.merchant_acct_key  
                        logger.debug('Valid granted outlet key for merchant acct')
                        
                        created_customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                         
                        if created_customer is None:
                            
                            
                            email           = existing_user_acct.email
                            mobile_phone    = existing_user_acct.mobile_phone
                            
                            logger.debug('email=%s', email)
                            logger.debug('mobile_phone=%s', mobile_phone)
                            
                            checking_customer = Customer.get_by_email(email, merchant_acct=merchant_acct) 
                            
                            if checking_customer:
                                is_email_used = True
                            else:
                                if is_not_empty(mobile_phone):
                                    checking_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
                                    if checking_customer:
                                        is_mobile_phone_used = True
                            
                            logger.debug('is_email_used=%s', is_email_used)
                            logger.debug('is_mobile_phone_used=%s', is_mobile_phone_used)
                            
                            if is_email_used == False and is_mobile_phone_used == False:
                            
                                created_customer = Customer.create_from_user(outlet, existing_user_acct, merchant_reference_code=merchant_reference_code)
                        
                            
                        logger.debug('created_customer=%s', created_customer)
                        
                    else:
                        logger.warn('Invalid granted outlet key or merchant account id')
                
                if created_customer:
                    
                    
                    
                    response_data = {
                                    'customer_key'              : created_customer.key_in_str,
                                    'registered_datetime'       : created_customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'merchant_reference_code'   : created_customer.merchant_reference_code,
                                    'reference_code'            : created_customer.reference_code,
                                    'merchant_account_key'      : merchant_act_key,
                                    'company_name'              : merchant_acct.company_name,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct),
                                    }
                    
                    response_data.update(user_details_dict(existing_user_acct))
                    
                    logger.debug('register_user_as_customer debug: response_data=%s', response_data)
                    
                    return create_rest_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    if is_email_used==True:
                        return create_rest_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                    
                    elif is_mobile_phone_used==True:
                        return create_rest_message('Mobile phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    else:
                        return create_rest_message('Failed to register customer', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_rest_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register customer due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

def user_details_dict(user_acct):
    is_email_verified           = user_acct.is_email_verified
    is_mobile_phone_verified    = user_acct.is_mobile_phone_verified
    
    logger.debug('user_details_dict debug: is_email_verified=%s', is_email_verified)
    logger.debug('user_details_dict debug: is_mobile_phone_verified=%s', is_mobile_phone_verified)
    
    email_vc_expiry_datetime            = None
    mobile_phone_vc_expiry_datetime     = None
    
    email_verified_datetime             = None
    mobile_phone_verified_datetime      = None
    
    if is_email_verified == False and user_acct.email_vc_expiry_datetime is not None:
        email_vc_expiry_datetime = user_acct.email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') 
    else:
        if user_acct.email_verified_datetime is not None:
            email_verified_datetime = user_acct.email_verified_datetime.strftime('%d-%m-%Y %H:%M:%S') 
            
    if is_mobile_phone_verified == False and user_acct.mobile_phone_vc_expiry_datetime is not None:
        mobile_phone_vc_expiry_datetime = user_acct.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S')
    else:
        if user_acct.mobile_phone_verified_datetime is not None:
            mobile_phone_verified_datetime = user_acct.mobile_phone_verified_datetime.strftime('%d-%m-%Y %H:%M:%S')
        
    birth_date_str = None
    if is_not_empty(user_acct.birth_date):
        birth_date_str = user_acct.birth_date.strftime('%d-%m-%Y')
         
    
    status = user_acct.status
    
    #for imported customer case
    if is_empty(status):
        status = 'completedRegistration'
    
    user_details = {
                       'reference_code'                       : user_acct.reference_code, 
                       'name'                                 : user_acct.name, 
                       'email'                                : user_acct.email,
                       'gender'                               : user_acct.gender,
                       'is_email_verified'                    : is_email_verified,
                       'is_mobile_phone_verified'             : is_mobile_phone_verified,
                       'status'                               : status,
                    }
    
    if is_not_empty(user_acct.mobile_phone):
        user_details['mobile_phone'] = user_acct.mobile_phone
        
    if is_not_empty(birth_date_str):
        user_details['birth_date'] = birth_date_str    
    
    if is_not_empty(email_vc_expiry_datetime):
        user_details['email_vc_expiry_datetime'] = email_vc_expiry_datetime
        
    if is_not_empty(mobile_phone_vc_expiry_datetime):
        user_details['mobile_phone_vc_expiry_datetime'] = mobile_phone_vc_expiry_datetime
        
    
    if is_not_empty(email_verified_datetime):
        user_details['email_verified_datetime'] = email_verified_datetime
        
    if is_not_empty(mobile_phone_verified_datetime):
        user_details['mobile_phone_verified_datetime'] = mobile_phone_verified_datetime        
    
    return user_details
    
@user_api_bp.route('/customer/<reference_code>', methods=['GET'])
def read_user_customer_acct(reference_code):
    logger.debug('read_user_customer_acct: reference_code=%s', reference_code)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_user_as_customer")
            
            customer                = None
            outlet_key              = request.headers.get('x-outlet-key')
            merchant_acct           = None
            existing_user_acct      = None
            
            logger.debug('outlet_key=%s', outlet_key)
            
            with db_client.context():
                outlet          = Outlet.fetch(outlet_key)
                    
                if outlet:
                    merchant_acct = outlet.merchant_acct_entity    
                    logger.debug('outlet.merchant_acct_key=%s', outlet.merchant_acct_key)
                    
                    
                    customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                    existing_user_acct = User.get_by_reference_code(reference_code)
                     
                else:
                    logger.warn('Invalid granted outlet key or merchant account id')
                
                if customer:
                    
                    response_data = {
                                    'customer_key'              : customer.key_in_str,
                                    'registered_datetime'       : customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'merchant_reference_code'   : customer.merchant_reference_code,
                                    'reference_code'            : customer.reference_code,
                                    'merchant_account_key'      : customer.registered_merchant_acct_key,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct), 
                                    }
                    
                    response_data.update(user_details_dict(existing_user_acct))
                    
                    logger.debug('read_user_customer_acct debug: response_data=%s', response_data)
                    
                    return create_rest_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    return create_rest_message('Customer account not found', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_rest_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to read customer details due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    

@user_api_bp.route('/customer/<customer_key>/reward/summary', methods=['GET'])
@user_auth_token_required
@elapsed_time_trace(trace_key="read_customer_reward_summary")
def read_customer_reward_summary(reference_code, customer_key):
    logger.debug('reference_code=%s', reference_code)
    #vouchers_list   = []
    tier_rewards    = []
    
    db_client = create_db_client(caller_info="read_customer_reward_summary")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            #customer_vouchers_list          = CustomerEntitledVoucher.list_all_by_customer(customer)
            customer_tier_reward_summary    = CustomerEntitledTierRewardSummary.list_tier_reward_summary_by_customer(customer)
            CustomerPointReward.list_by_customer(customer)
            '''
            if customer_vouchers_list:
                for v in customer_vouchers_list:
                    vouchers_list.append(v.to_dict())
            '''        
            if customer_tier_reward_summary:
                for v in customer_tier_reward_summary:
                    tier_rewards.append(v.to_dict())
    
    
    
    result = {
            'reference_code'                        : reference_code,
            #'vouchers'          : vouchers_list,
            'tier_rewards'                          : tier_rewards,
            'reward_summary'                        : customer.reward_summary,
            'prepaid_summary'                       : customer.prepaid_summary,
            'entitled_voucher_summary'              : customer.entitled_voucher_summary,
            'entitled_lucky_draw_ticket_summary'    : customer.entitled_lucky_draw_ticket_summary,
            }
    
    return jsonify(result)
    
@user_api_bp.route('/check-auth-token', methods=['POST'])
@user_auth_token_required
def check_auth_token(reference_code):
    
    db_client = create_db_client(caller_info="check_auth_token")
    
    with db_client.context():
        user_acct = User.get_by_reference_code(reference_code)
        user_auth_token     = request.headers.get('x-auth-token')
        
        response_data = {
                        'auth_token'              : user_auth_token,
                        }
        
        response_data.update(user_details_dict(user_acct))
    
    return create_rest_message(status_code=StatusCode.OK, **response_data)


    
@user_api_bp.route('/<reference_code>', methods=['GET'])
@user_auth_token_required
def read_user_acct(reference_code):
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="read_user_acct")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('read_user_acct: found user account by reference_code=%s', reference_code)    
            is_email_verified           = user_acct.is_email_verified
            is_mobile_phone_verified    = user_acct.is_email_verified
            
            email_vc_expiry_datetime             = None
            mobile_phone_vc_expiry_datetime      = None
            
            if is_email_verified == False:
                #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
                #email_vc_expiry_datetime = str(user_acct.email_vc_expiry_datetime)
                email_vc_expiry_datetime = user_acct.email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                
            if is_mobile_phone_verified == False:
                #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
                mobile_phone_vc_expiry_datetime = str(user_acct.mobile_phone_vc_expiry_datetime)    
                
            return create_rest_message(status_code=StatusCode.OK, 
                                       reference_code                       = user_acct.reference_code, 
                                       name                                 = user_acct.name, 
                                       email                                = user_acct.email, 
                                       is_email_verified                    = is_email_verified,
                                       is_mobile_phone_verified             = is_mobile_phone_verified,
                                       email_vc_expiry_datetime             = email_vc_expiry_datetime,
                                       mobile_phone_vc_expiry_datetime      = mobile_phone_vc_expiry_datetime,
                                       status                               = user_acct.status,
                                       )
        else:
            logger.debug('user account is not found')
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_user: user verify input is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@user_api_bp.route('/delete-account-request', methods=['DELETE'])
@user_auth_token_required
def delete_user_acct(reference_code):
    
    
    db_client = create_db_client(caller_info="delete_user_acct")
    
    password   = request.args.get('password') or request.form.get('password') or request.json.get('password')
    
    with db_client.context():
        user_acct = User.get_by_reference_code(reference_code)
    
    if user_acct:
        if user_acct.is_still_lock:
            return create_rest_message('User account is locked after many trials for security purpose. Please try after an hour.', status_code=StatusCode.BAD_REQUEST)
        else:
            if user_acct.is_valid_password(password):
                logger.debug('delete_user_acct: found user account by reference_code=%s', reference_code)
                if user_acct.demo_account==True:
                    return create_rest_message('Demo account is not allow to delete', status_code=StatusCode.BAD_REQUEST)
                else:
                    with db_client.context():
                        user_acct.request_to_delete() 
                    
                    return create_rest_message(status_code=StatusCode.ACCEPTED,)
            else:
                with db_client.context():
                    user_acct.add_try_count()
                
                return create_rest_message('Password is not match', status_code=StatusCode.BAD_REQUEST)
    
    else:
        logger.debug('user account is not found')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
          
    
@user_api_bp.route('/read-user-new-message-count', methods=['GET'])
@user_auth_token_required
def read_user_new_message_count(reference_code):
    logger.info('reference_code=%s', reference_code)
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="read_user_new_message_count")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            return create_rest_message(status_code=StatusCode.OK, 
                                       new_message_count = user_acct.new_message_count
                                       )
        else:
            logger.debug('user account is not found')
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_user: user verify input is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)        

@user_api_bp.route('/joined-brands-list', methods=['GET'])
@user_auth_token_required
def list_joined_brands(reference_code):
    
    limit           = request.args.get('limit')
    start_cursor    = request.args.get('start_cursor')
    
    logger.debug('limit=%s', limit)
    logger.debug('start_cursor=%s', start_cursor)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_joined_brands")
        brands_list     = []
        user_acct       = None
        result_data     = {}
        
        if is_not_empty(limit):
            limit = int(limit)
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)
            
            
            
            with db_client.context():
                (customer_accts_list, next_cursor) = Customer.list_paginated_by_user_account(user_acct, start_cursor=start_cursor, limit=limit)
                
                for customer_acct in customer_accts_list:
                    merchant_acct = customer_acct.registered_merchant_acct
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'account_id': merchant_acct.account_code,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                '''
                new_brand_list = []
                for brand in brands_list:
                    new_brand_list.append({
                                        'key'       : brand['key'],
                                        'account_id': brand['account_id'],
                                        'name'      : random_string(10),
                                        'logo_url'  : brand['logo_url'],
                                        
                                        })
                    new_brand_list.append({
                                        'key'       : brand['key'],
                                        'account_id': brand['account_id'],
                                        'name'      : random_string(10),
                                        'logo_url'  : brand['logo_url'],
                                        
                                        })
                    
                    new_brand_list.append({
                                        'key'       : brand['key'],
                                        'account_id': brand['account_id'],
                                        'name'      : random_string(10),
                                        'logo_url'  : brand['logo_url'],
                                        
                                        })
                    
                '''                       
                result_data= {
                                'result'        : brands_list,
                                'count'         : len(brands_list),
                                }
                  
                if is_not_empty(next_cursor):
                    result_data['next_cursor'] = next_cursor  
        
        
        
        return create_rest_message(status_code=StatusCode.OK,
                                   **result_data, 
                                   )
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@user_api_bp.route('/all-joined-brands-list', methods=['GET'])
@user_auth_token_required
def list_all_joined_brands(reference_code):
    
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_all_joined_brands")
        brands_list     = []
        user_acct       = None
        result_data     = {}
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)
            
            
            
            with db_client.context():
                customer_accts_list = Customer.list_by_user_account(user_acct)
                
                for customer_acct in customer_accts_list:
                    merchant_acct = customer_acct.registered_merchant_acct
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'account_id': merchant_acct.account_code,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                                     
                result_data= {
                                'result'        : brands_list,
                                'count'         : len(brands_list),
                                }
                  
        
        return create_rest_message(status_code=StatusCode.OK,
                                   **result_data, 
                                   )
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)       
    
@user_api_bp.route('/reset-email-vc', methods=['PUT'])
def reset_email_verification_code():
    email = request.args.get('email') or request.form.get('email') or request.json.get('email')
    
    logger.info('reset_email_verification_code: going to reset email verification code by email=%s', email)
    
    if is_not_empty(email):
        db_client = create_db_client(caller_info="reset_email_verification_code")
        user_acct = None
        
        
        
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct is None:
            '''
            logger.debug('reset_email_verification_code: found user account by email=%s', email)    
            is_email_verified           = user_acct.is_email_verified
            
            logger.debug('reset_email_verification_code: is_email_verified=%s', is_email_verified)
            
            email_vc_expiry_datetime = None
            
            with db_client.context():
                user_acct.reset_email_vc()
            
            email_vc_expiry_datetime = user_acct.email_vc_expiry_datetime
            '''
            
            
            #email_vc_expiry_datetime    = datetime.utcnow() + timedelta(minutes=10)
            email_vc_expiry_datetime    = _generate_email_expiry_datetime()
            email_vc                    = random_number(6)
            email_vc_prefix             = random_string(4, is_human_mistake_safe=True)
            
            send_email_verification_code_email(email, email_vc, email_vc_prefix)
            
            logger.info('reset_email_verification_code: email_vc_expiry_datetime=%s', email_vc_expiry_datetime)
            logger.info('reset_email_verification_code: verification code=%s', email_vc)
                
            return create_rest_message(status_code=StatusCode.OK, 
                                       #email_vc_expiry_datetime          = str(email_vc_expiry_datetime),
                                       expiry_datetime     = email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                       prefix              = email_vc_prefix, 
                                       code                = email_vc,
                                       
                                       )
        else:
            reference_code = request.headers.get('x-reference-code')
            logger.debug('reference_code from header=%s', reference_code)
            logger.debug('reference_code from database=%s', user_acct.reference_code)
            
            if reference_code == user_acct.reference_code:
                email_vc_expiry_datetime    = _generate_email_expiry_datetime()
                email_vc                    = random_number(6)
                email_vc_prefix             = random_string(4, is_human_mistake_safe=True)
                
                send_email_verification_code_email(email, email_vc, email_vc_prefix)
                
                return create_rest_message(status_code=StatusCode.OK, 
                                       #email_vc_expiry_datetime          = str(email_vc_expiry_datetime),
                                       expiry_datetime      = email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                       prefix               = email_vc_prefix,
                                       code                 = email_vc,
                                       )
            else:
                return create_rest_message('The email have been taken %s' % email, status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('reset_email_verification_code: reference code is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 

def _generate_email_expiry_datetime():
    return datetime.utcnow() + timedelta(minutes=int(os.environ.get('EMAIL_EXPIRY_LENGTH_IN_MINUTE')))
    
@user_api_bp.route('/reset-mobile-phone-vc', methods=['PUT'])
@user_auth_token_required
def reset_mobile_phone_verification_code(reference_code):
    mobile_phone = request.args.get('mobile_phone') or request.form.get('mobile_phone') or request.json.get('mobile_phone')

    logger.debug('mobile_phone=%s', mobile_phone)
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(mobile_phone):
        db_client                           = create_db_client(caller_info="reset_mobile_phone_verification_code")
        user_acct                           = None
        
        with db_client.context():
            user_by_mobile_phone    = User.get_by_mobile_phone(mobile_phone)
        
            logger.debug('user_by_mobile_phone=%s', user_by_mobile_phone)
        
        if user_by_mobile_phone is not None:
            if reference_code==user_by_mobile_phone.reference_code:
                #logger.debug('reset_mobile_phone_verification_code: found user account by mobile_phone=%s', mobile_phone)    
                #is_mobile_phone_verified           = user_acct.is_mobile_phone_verified
                
                with db_client.context():
                    user_by_mobile_phone.reset_mobile_phone_vc()
                    
                logger.debug('reset_mobile_phone_verification_code: mobile_phone_vc_expiry_datetime=%s', user_by_mobile_phone.mobile_phone_vc_expiry_datetime)
                logger.debug('reset_mobile_phone_verification_code: verification code=%s', user_by_mobile_phone.mobile_phone_vc)   
                
                mobile_phone_vc_prefix             = random_string(4, is_human_mistake_safe=True)
                
                send_mobile_phone_verification_code_sms(mobile_phone, user_by_mobile_phone.mobile_phone_vc, mobile_phone_vc_prefix)
                
                return create_rest_message(status_code=StatusCode.OK, 
                                           expiry_datetime      = user_by_mobile_phone.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                           code                 = user_by_mobile_phone.mobile_phone_vc,
                                           prefix               = mobile_phone_vc_prefix,
                                           )
            else:
                return create_rest_message(gettext('Mobile phone have been taken'), status_code=StatusCode.BAD_REQUEST)
        else:
            with db_client.context():
                user_acct    = User.get_by_reference_code(reference_code)
            
            if user_acct is not None:
                with db_client.context():
                    user_acct.reset_mobile_phone_vc()
                    
                mobile_phone_vc_prefix             = random_string(4, is_human_mistake_safe=True)
                
                logger.debug('reset_mobile_phone_verification_code: mobile_phone_vc_expiry_datetime=%s', user_acct.mobile_phone_vc_expiry_datetime)
                logger.debug('reset_mobile_phone_verification_code: verification code=%s', user_acct.mobile_phone_vc)    
                
                send_mobile_phone_verification_code_sms(mobile_phone, user_acct.mobile_phone_vc, mobile_phone_vc_prefix)
                
                return create_rest_message(status_code=StatusCode.OK, 
                                           expiry_datetime      = user_acct.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                           code                 = user_acct.mobile_phone_vc,
                                           prefix               = mobile_phone_vc_prefix,
                                           
                                           )
            else:
                return create_rest_message(gettext('Invalid input'), status_code=StatusCode.BAD_REQUEST)
                
                
    else:
        logger.warn('reset_mobile_phone_verification_code: mobile phone is invalid')
        return create_rest_message(gettext('Missing mobile phone'), status_code=StatusCode.BAD_REQUEST)  
    
@user_api_bp.route('/change-password', methods=['PUT'])
@user_auth_token_required
def change_password(reference_code):
    
    existing_password   = request.args.get('existing_password') or request.form.get('existing_password') or request.json.get('existing_password')
    new_password        = request.args.get('new_password') or request.form.get('new_password') or request.json.get('new_password')
    
    if is_not_empty(existing_password) and is_not_empty(new_password):
        db_client = create_db_client(caller_info="change_password")
        user_acct = None
        is_existing_password_valid = False
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('change_password: found user account by reference_code=%s', reference_code)    
            logger.debug('change_password: existing_password=%s', existing_password)
            logger.debug('change_password: new_password=%s', new_password)
            
            with db_client.context():
                if user_acct.is_valid_password(existing_password):
                    is_existing_password_valid = True
                    user_acct.change_password(new_password)
                
        if is_existing_password_valid:    
            return create_rest_message(
                                    status_code=StatusCode.OK
                                       
                                       )
        else:
            return create_rest_message('existing password is not valid', status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_rest_message('Missing password input', status_code=StatusCode.BAD_REQUEST)  
    
@user_api_bp.route('/set-password', methods=['PUT'])
def set_password():
    
    new_password        = request.args.get('new_password') or request.form.get('new_password') or request.json.get('new_password')
    reset_password_token = request.args.get('reset_password_token') or request.form.get('reset_password_token') or request.json.get('reset_password_token')
    
    logger.debug('set_password debug: new_password=%s', new_password)
    logger.debug('set_password debug: reset_password_token=%s', reset_password_token)
    
    if is_not_empty(new_password) and is_not_empty(reset_password_token):
        db_client = create_db_client(caller_info="set_password")
        user_acct = None
        
        
        with db_client.context():
            user_acct = User.get_by_reset_password_token(reset_password_token)
        
        if user_acct:
            logger.debug('set_password: found user account by reset_password_token=%s', user_acct)    
            
            
            with db_client.context():
                user_acct.change_password(new_password)
                
            
            return create_rest_message(
                                    status_code=StatusCode.OK
                                       
                                       )
        else:
            return create_rest_message('Invalid request to set password', status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_rest_message('Missing password input', status_code=StatusCode.BAD_REQUEST)          
    
@user_api_bp.route('/request-reset-password-via-email', methods=['POST'])
def request_reset_password_via_email_post():
    email = request.args.get('email') or request.form.get('email') or request.json.get('email')
    
    logger.debug('reset_password_request_post: going to reset email verification code by email=%s', email)
    
    if is_not_empty(email):
        db_client = create_db_client(caller_info="reset_email_verification_code")
        user_acct = None
        
        
        
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            logger.debug('request_reset_password_via_email_post: found user account by email=%s', email)    
            is_email_verified           = user_acct.is_email_verified
            
            logger.debug('request_reset_password_via_email_post: is_email_verified=%s', is_email_verified)
            
            #if is_email_verified:
            with db_client.context():
                user_acct.reset_password_request()
            
            send_reset_password_request_email(user_acct)
                
            return create_rest_message(status_code=StatusCode.OK
                                       
                                       )
        else:
            return create_rest_message('Cannot find user by email %s' % email, status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('reset_password_post: email is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@user_api_bp.route('/request-reset-password-via-mobile-phone', methods=['POST'])
def request_reset_password_via_mobile_phone_post():
    mobile_phone = request.args.get('mobile_phone') or request.form.get('mobile_phone') or request.json.get('mobile_phone')
    
    logger.debug('request_reset_password_via_mobile_phone_post: going to reset mobile_phone verification code by mobile phone=%s', mobile_phone)

    logger.debug('mobile_phone=%s', mobile_phone)
    
    if is_not_empty(mobile_phone):
        db_client                           = create_db_client(caller_info="request_reset_password_via_mobile_phone_post")
        
        with db_client.context():
            user_by_mobile_phone    = User.get_by_mobile_phone(mobile_phone)
        
            logger.debug('user_by_mobile_phone=%s', user_by_mobile_phone)
        
        if user_by_mobile_phone is not None:
            with db_client.context():
                user_by_mobile_phone.reset_mobile_phone_vc()
                
                
                
            logger.debug('request_reset_password_via_mobile_phone_post debug: mobile_phone_vc_expiry_datetime=%s', user_by_mobile_phone.mobile_phone_vc_expiry_datetime)
            logger.debug('request_reset_password_via_mobile_phone_post debug: verification code=%s', user_by_mobile_phone.mobile_phone_vc)   
            
            mobile_phone_vc_prefix             = random_string(4, is_human_mistake_safe=True)
            
            send_mobile_phone_verification_code_sms(mobile_phone, user_by_mobile_phone.mobile_phone_vc, mobile_phone_vc_prefix)
            
            with db_client.context():
                reset_password_token = '%s-%s' % (mobile_phone_vc_prefix, user_by_mobile_phone.mobile_phone_vc)
                logger.debug('request_reset_password_via_mobile_phone_post debug: reset_password_token=%s', reset_password_token)
                user_by_mobile_phone.set_reset_password_token(reset_password_token)
            
            return create_rest_message(status_code=StatusCode.OK, 
                                       expiry_datetime      = user_by_mobile_phone.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                       code                 = user_by_mobile_phone.mobile_phone_vc,
                                       prefix               = mobile_phone_vc_prefix,
                                       is_invalid_account   = False,
                                       )
        else:
            return create_rest_message(status_code=StatusCode.OK, is_invalid_account=True,)
                
                
    else:
        logger.warn('request_reset_password_via_mobile_phone_post: mobile phone is invalid')
        return create_rest_message(gettext('Missing mobile phone'), status_code=StatusCode.BAD_REQUEST) 
    

@user_api_bp.route('/outlet-reviews', methods=['POST'])
@user_auth_token_required
def outlet_reviews(reference_code):
    logger.debug('---outlet_reviews---')
    logger.debug('outlet_reviews: reference_code=%s', reference_code)
    try:
        reviews_data_in_json   = request.get_json()
        logger.debug('outlet_reviews: reviews_data_in_json=%s', reviews_data_in_json)
        
        reviews_data_form  = OutletReviewsForm(ImmutableMultiDict(reviews_data_in_json))
        
        if reviews_data_form.validate():
            food_score              = reviews_data_form.food_score.data
            service_score           = reviews_data_form.service_score.data
            ambience_score          = reviews_data_form.ambience_score.data
            value_for_money_score   = reviews_data_form.value_for_money_score.data
            
            logger.debug('outlet_reviews: food_score=%s', food_score)
            logger.debug('outlet_reviews: service_score=%s', service_score)
            logger.debug('outlet_reviews: ambience_score=%s', ambience_score)
            logger.debug('outlet_reviews: value_for_money_score=%s', value_for_money_score)
            
            return create_rest_message(status_code=StatusCode.OK)
        
        else:
            logger.warn('outlet_reviews: outlet reviews input is invalid')
            error_message = reviews_data_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        return create_rest_message('Failed to process outlet reviews', status_code=StatusCode.BAD_REQUEST)   
        
@user_api_bp.route('/voucher/<redeem_code>/remove', methods=['DELETE'])
@user_auth_token_required
def remove_user_voucher(reference_code, redeem_code):
    logger.info('reference_code=%s', reference_code)
    logger.info('redeem_code=%s', redeem_code)
        
    if is_not_empty(redeem_code):
        #reference_code = request.headers.get('x-reference-code')
        
        db_client = create_db_client(caller_info="remove_user_voucher")
        with db_client.context():
            customer_voucher    = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
            
            if customer_voucher: 
                
                customer_voucher.remove()  
                customer = customer_voucher.entitled_customer_acct
                customer.update_after_removed_voucher(customer_voucher)
            else:
                logger.info('voucher is not found')    

        if customer_voucher and customer_voucher.is_removed:        
            return create_rest_message(status_code=StatusCode.OK)
        else:
            logger.info('Invalid voucher redeem code')
            return create_rest_message('Invalid voucher redeem code', status_code=StatusCode.BAD_REQUEST)
    else:
        logger.info('Missing voucher redeem code')
        return create_rest_message('Missing voucher redeem code', status_code=StatusCode.BAD_REQUEST)

def send_email_verification_code_email(email, verification_code, request_id):
    message = '''
                Dear,
                
                Please enter below code to verify your email for {mobile_app_name}.
                
                
                {request_id}-{verification_code}
                
                
                The code will be expired after {email_expiry_in_minute} minutes.
                
                Cheers,
                {application_name} Team
                
                
                ***Please do not reply to this email. This is an auto-generated email.***
    
            '''.format(email=email, verification_code=verification_code, 
                       application_name=APPLICATION_NAME,
                       mobile_app_name=MOBILE_APP_NAME,
                       request_id = request_id, 
                       email_expiry_in_minute=os.environ.get('EMAIL_EXPIRY_LENGTH_IN_MINUTE'))
    
    subject      = 'Email Verification from {mobile_app_name}'.format(mobile_app_name=MOBILE_APP_NAME)
    
    logger.info('DEPLOYMENT_MODE=%s', DEPLOYMENT_MODE)
    
    logger.info(message)
    
    if DEPLOYMENT_MODE==PRODUCTION_MODE:
        trigger_send_email(recipient_address = email, subject=subject, message=message)
    else:
        logger.debug('not send email for development or local mode')
        
        
def send_mobile_phone_verification_code_sms(mobile_phone, verification_code, request_id):
    message = '{mobile_app_name} {request_id}-{verification_code} is your Verification Code. It will be expired after {expiry_in_minute} minutes'.format(mobile_app_name=MOBILE_APP_NAME, verification_code=verification_code, 
                       request_id = request_id, 
                       expiry_in_minute=os.environ.get('MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE'))
    
    logger.info('DEPLOYMENT_MODE=%s', DEPLOYMENT_MODE)
    
    logger.info('sms message: %s', message)
    
    if DEPLOYMENT_MODE in (PRODUCTION_MODE, DEMO_MODE):
        logger.info('Going to send sms to %s', mobile_phone)
        send_sms(to_number=mobile_phone, body=message)
    else:
        logger.debug('not send sms for development or local mode')

    
def send_reset_password_request_email(user_acct):
    reset_password_link = '{base_url}/user/reset-password-request/{request_reset_password_token}'.format(base_url=APPLICATION_BASE_URL, request_reset_password_token=user_acct.request_reset_password_token)
    
    message = '''
                Dear {name},
                
                
                Forgot your password? No worries.
                We received your request to reset the password for your {mobile_app_name} account. 
                
                Just one more step to reset the password, please click the below link:
                
                
                {reset_password_link}
                
                
                
                Or copy and paste the URL into your web browser.
                
                Cheers,
                {application_name} Team
                
                
                ***Please do not reply to this email. This is an auto-generated email.***
    
            '''.format(name=user_acct.name, email=user_acct.email, 
                       reset_password_link=reset_password_link, 
                       application_name=APPLICATION_NAME,
                       mobile_app_name=MOBILE_APP_NAME,
                       )
    
    subject = 'Request to reset password fors {mobile_app_name}'.format(mobile_app_name=MOBILE_APP_NAME,application_name=APPLICATION_NAME)
    
    logger.info('email message: %s', message)
            
    trigger_send_email(recipient_address = user_acct.email, subject=subject, message=message)
    '''
    send_email(sender           = DEFAULT_SENDER, 
                   to_address   = [user_acct.email], 
                   subject      = subject, 
                   body         = message,
                   app          = current_app
                   )    
    ''' 

def send_reset_password_request_sms(mobile_phone, verification_code, request_id):
    message = '{mobile_app_name} {request_id}-{verification_code} is your Verification Code. It will be expired after {expiry_in_minute} minutes'.format(mobile_app_name=MOBILE_APP_NAME, verification_code=verification_code, 
                       request_id = request_id, 
                       expiry_in_minute=os.environ.get('MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE'))
    
    logger.info('DEPLOYMENT_MODE=%s', DEPLOYMENT_MODE)
    
    logger.info('sms message: %s', message)
    
    if DEPLOYMENT_MODE in (PRODUCTION_MODE, DEMO_MODE):
        logger.info('Going to send sms to %s', mobile_phone)
        send_sms(to_number=mobile_phone, body=message)
    else:
        logger.debug('not send sms for development or local mode')
        
@user_api_bp.route('/list-user-messages', methods=['GET'])
@user_auth_token_required
def list_user_messages(reference_code):
    
    limit           = request.args.get('limit')
    start_cursor    = request.args.get('start_cursor')
    
    logger.debug('limit=%s', limit)
    logger.debug('start_cursor=%s', start_cursor)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_user_messages")
        user_acct               = None
        user_messages_list      = []
        result_data             = {}
        
        if is_not_empty(limit):
            limit = int(limit)
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)
            
            
            
            with db_client.context():
                (messages_list, next_cursor) = Message.list_paginated_by_user_account(user_acct, start_cursor=start_cursor, limit=limit)
                
                for message in messages_list:
                    logger.debug('message.created_datetime=%s', message.created_datetime)
                    local_datetime = from_utc_datetime_to_local_datetime(message.created_datetime, country_code=user_acct.country,)
                    
                    user_messages_list.append(
                                {
                                'message_key'       : message.key_in_str,
                                'message_title'     : message.title,
                                'message_category'  : message.message_category,
                                'message_content'   : message.message_content,
                                'message_data'      : message.message_data,
                                'message_status'    : message.status,
                                #'message_status'    : 'n',
                                'created_datetime'  : local_datetime.strftime('%d-%m-%Y %H:%M'),
                                }
                                )
                    
                
                result_data= {
                                'result'        : user_messages_list,
                                'count'         : len(user_messages_list),
                                }
                logger.debug('result_data=%s', result_data)
                  
                if is_not_empty(next_cursor):
                    result_data['next_cursor'] = next_cursor  
        
        
        
        return create_rest_message(status_code=StatusCode.OK,
                                   **result_data, 
                                   )
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)          
    

@user_api_bp.route('/read-user-message', methods=['POST'])
@user_auth_token_required
def read_user_message(reference_code):
    logger.info('reference_code=%s', reference_code)
    message_key = request.args.get('message_key') or request.form.get('message_key') or request.json.get('message_key')
    
    if is_not_empty(message_key):
        db_client = create_db_client(caller_info="update_user_message_as_read")
        
        with db_client.context():
            Message.update_read(message_key)

        return create_rest_message(status_code=StatusCode.ACCEPTED,)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
 
@user_api_bp.route('/delete-user-message', methods=['DELETE'])
@user_auth_token_required
def delete_user_message_as_read(reference_code):
    logger.info('reference_code=%s', reference_code)
    message_key = request.args.get('message_key') or request.form.get('message_key') or request.json.get('message_key')
    
    if is_not_empty(message_key):
        db_client = create_db_client(caller_info="delete_user_message_as_read")
        
        with db_client.context():
            Message.update_delete(message_key)
            
        return create_rest_message(status_code=StatusCode.ACCEPTED,)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/update-device-details', methods=['PUT'])
@user_auth_token_required
def update_device_details(reference_code):
    platform        = request.args.get('platform') or request.form.get('platform') or request.json.get('platform')
    device_token    = request.args.get('device_token') or request.form.get('device_token') or request.json.get('device_token')

    logger.info('platform=%s', platform)
    logger.info('device_token=%s', device_token)
    
    if is_not_empty(platform) and is_not_empty(device_token):
        db_client                           = create_db_client(caller_info="update_device_details")
        user_acct                           = None
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
            
            user_acct.update_device_details(platform, device_token)
            
        
        if user_acct:
            logger.debug('update_device_details: found user account by reference_code=%s', reference_code)
            return create_rest_message(status_code=StatusCode.ACCEPTED)
        
        else:
            return create_rest_message('Invalid user data', status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message('Missing required data', status_code=StatusCode.BAD_REQUEST)
    