import logging

import utils
from common import SimpleClient

__author__ = "Lucas Cristiano Calixto Dantas"
__copyright__ = "Copyright 2017, Lucas Cristiano Calixto Dantas"
__credits__ = ["Lucas Cristiano Calixto Dantas"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Lucas Cristiano Calixto Dantas"
__email__ = "lucascristiano27@gmail.com"
__status__ = "Development"


class FiwareContextClient(SimpleClient):

    def __init__(self, config_file):
        super().__init__(config_file)

        config_dict = utils.read_config_file(config_file)

        self.sth_host = config_dict['sth_host']
        self.sth_port = config_dict['sth_port']

        self.cygnus_host = config_dict['cygnus_host']
        self.cygnus_notification_host = config_dict['cygnus_notification_host']
        self.cygnus_port = config_dict['cygnus_port']

        self.perseo_host = config_dict['perseo_host']
        self.perseo_port = config_dict['perseo_port']

    def get_entity_by_id(self, entity_id):
        """
        Queries an entity information give its entity id
        :param entity_id: The id of the entity to be searched
        :return: The information of the entity found with the given id or None if no entity was found with the id
        """
        logging.info("Getting entity by id '{}'".format(entity_id))

        # TODO Remove hardcoded type from url
        url = "http://{}:{}/v2/entities/{}/attrs?type=thing".format(self.cb_host, self.cb_port, entity_id)

        payload = ''

        return self._send_request(url, payload, 'GET')

    def get_entities_by_type(self, entity_type):
        logging.info("Getting entities by type '{}'".format(type))

        url = "http://{}:{}/v2/entities?type={}".format(self.cb_host, self.cb_port, entity_type)
        payload = ''

        return self._send_request(url, payload, 'GET')

    def get_subscription_by_id(self, subscription_id):
        logging.info("Getting subscription by id '{}'".format(subscription_id))

        url = "http://{}:{}/v2/subscriptions/{}".format(self.cb_host, self.cb_port, subscription_id)

        payload = ''

        return self._send_request(url, payload, 'GET')

    def list_subscriptions(self):
        logging.info("Listing subscriptions")

        url = "http://{}:{}/v2/subscriptions".format(self.cb_host, self.cb_port)

        payload = ''

        return self._send_request(url, payload, 'GET')

    def unsubscribe(self, subscription_id):
        logging.info("Removing subscriptions")

        url = "http://{}:{}/v1/unsubscribeContext".format(self.cb_host, self.cb_port)
        
        additional_headers = {'Accept': 'application/json',
                              'Content-Type': 'application/json'}

        payload = {"subscriptionId": str(subscription_id)}

        return self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def subscribe_attributes_change(self, device_id, attributes, notification_url):
        logging.info("Subscribing for change on attributes '{}' on device with id '{}'".format(attributes, device_id))

        url = "http://{}:{}/v1/subscribeContext".format(self.cb_host, self.cb_port)

        additional_headers = {'Accept': 'application/json',
                              'Content-Type': 'application/json'}

        payload = {"entities": [{
            "type": "thing",
            "isPattern": "false",
            "id": str(device_id)
        }],
            "attributes": attributes,
            "notifyConditions": [{
                "type": "ONCHANGE",
                "condValues": attributes
            }],
            "reference": notification_url,
            "duration": "P1Y",
            "throttling": "PT1S"
        }

        return self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def subscribe_cygnus(self, entity_id, attributes):
        logging.info("Subscribing Cygnus")

        notification_url = "http://{}:{}/notify".format(self.cygnus_notification_host, self.cygnus_port)
        return self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def subscribe_historical_data(self, entity_id, attributes):
        logging.info("Subscribing to historical data")

        notification_url = "http://{}:{}/notify".format(self.sth_host, self.sth_port)
        return self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def create_attribute_change_rule(self, attribute, attribute_type, condition, notification_url, action='post'):
        logging.info("Creating attribute change rule")

        url = "http://{}:{}/rules".format(self.perseo_host, self.perseo_port)

        additional_headers = {'Accept': 'application/json',
                              'Content-Type': 'application/json'}

        rule_template = "select *,\"{}-rule\" as ruleName from pattern " \
                        "[every ev=iotEvent(cast(cast(ev.{}?,String),{}){})]"
        payload = {
            "name": "{}-rule".format(attribute),
            "text": rule_template.format(attribute, attribute, attribute_type, condition),
            "action": {
                "type": "",
                "template": "Alert! {0} is now ${{ev.{1}}}.".format(attribute, attribute),
                "parameters": {}
            }
        }

        if action == 'email':
            payload["action"]["type"] = "email"
            # TODO Remove hardcoded info
            payload["action"]["parameters"] = {"to": "{}".format("lucascristiano27@gmail.com"),
                                               "from": "{}".format("lucas.calixto.dantas@gmail.com"),
                                               "subject": "Alert! High {} Detected".format(attribute.capitalize())}
        elif action == 'post':
            payload["action"]["type"] = "post"
            payload["action"]["parameters"] = {"url": "{}".format(notification_url)}

        else:
            error_msg = "Unknown action '{}'".format(action)
            logging.error(error_msg)
            return {'error': error_msg}

        return self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def get_historical_data(self, entity_type, entity_id, attribute, items_number=10):
        logging.info("Getting historical data")

        url = "http://{}:{}/STH/v1/contextEntities/type/{}/id/{}/attributes/{}?lastN={}".format(self.sth_host,
                                                                                                self.sth_port,
                                                                                                entity_type,
                                                                                                entity_id,
                                                                                                attribute,
                                                                                                items_number)

        additional_headers = {'Accept': 'application/json',
                              'Fiware-Service': str(self.fiware_service).lower(),
                              'Fiware-ServicePath': str(self.fiware_service_path).lower()}

        payload = ''

        return self._send_request(url, payload, 'GET', additional_headers=additional_headers)
