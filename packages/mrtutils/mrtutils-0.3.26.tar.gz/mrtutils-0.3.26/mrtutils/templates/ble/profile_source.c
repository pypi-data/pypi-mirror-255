/**
 * @file ${obj.name.lower()}_profile.h
 * @brief ${obj.desc}
 * @date ${obj.genTime}
 * 
 */

/* Includes ------------------------------------------------------------------*/
#include "${obj.name.lower()}_profile.h"


/*user-block-top-start*/
/*user-block-top-end*/

/* Private Variables ---------------------------------------------------------*/
MRT_GATT_DATA_ATTR ${obj.name.lower()}_profile_t ${obj.name}_profile;


/* Functions -----------------------------------------------------------------*/

mrt_status_t ${obj.name.lower()}_profile_init(void* ctx)
{
    mrt_gatt_init_pro(&${obj.name}_profile.mPro, ${len(obj.services)}, 0, "${obj.name}");

    //Set Context Pointer
    ${obj.name}_profile.mPro.ctx = ctx;
    
    /* Initialize all services */
    %for svc in obj.services:
    ${"{0}_profile.m{1} = {2}_svc_init(&{0}_profile.mPro);".format(obj.name.lower(),t.camelCase(svc.name), svc.prefix)}
    %endfor


    /*user-block-init-start*/
    /*user-block-init-end*/
    
    return MRT_STATUS_OK;
}

mrt_status_t ${obj.name.lower()}_profile_register(void)
{
    mrt_status_t status;



    for(uint16_t i =0; i < ${obj.name}_profile.mPro.svcCount; i++ )
    {
        status = mrt_gatt_register_svc(${obj.name}_profile.mPro.svcs[i]);
        if(status != MRT_STATUS_OK)
        {
            break;
        }

    }

    /* Call post-registration handlers */
    %for svc in obj.services:
    ${"{0}_svc_post_registration_handler();".format(svc.prefix)}
    %endfor

    /*user-block-register-start*/
    /*user-block-register-end*/

    return status;
}

mrt_status_t ${obj.name.lower()}_profile_handle_evt(mrt_gatt_evt_t* evt)
{


    if(evt->chr == NULL)
    {
        return MRT_STATUS_OK;
    }

    //If it is a CCCD write, update the CCCD fpr the characteristic
    if((evt->type == MRT_GATT_EVT_CCCD_WRITE) )
    {
        evt->chr->cccd = *((uint16_t*)evt->data.value);
    }

    /**
     * ** BY DEFAULT WE ONLY PASS WRITE EVENTS TO THE CHARACTERISTIC CALLBACK HANDLERS **
     * To pass all events to the handler, comment out the following line
     */
    if(evt->type != MRT_GATT_EVT_VALUE_WRITE){return MRT_STATUS_OK;}

    
    //By default only call the event callback for write events because READ events are auto-response by default
    if((evt->chr != NULL) && (evt->type != MRT_GATT_EVT_NONE))
    {
        //ESP_LOGE(GATT_ADAPTER_TAG, "CALLBACK  Event Type: %04X", evt->type );
        evt->status = evt->chr->cbEvent(evt);
    }

    /*user-block-profile-handler-start*/
    /*user-block-profile-handler-end*/



    return MRT_STATUS_OK;
}



/*user-block-functions-start*/
/*user-block-functions-end*/

