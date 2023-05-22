#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackClient:
    def __init__(self):
        self.client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
        self.channel_id = os.environ['SLACK_CHANNEL_ID']

    def post_message(self, message):
        try:
            response = self.client.chat_postMessage(channel=self.channel_id, text=message)
            assert response["message"]["text"] == message
        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")


# In[2]:


def test_slack():
    slack_client = SlackClient()
    slack_client.post_message('Hello, world!')


# In[3]:


test_slack()


# In[4]:


import openai

class OpenAIClient:
    def __init__(self):
        openai.api_key = os.environ['OPENAI_KEY']

    def get_response(self, prompt, max_tokens=150):
        try:
            response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=max_tokens)
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error in generating response: {str(e)}")
            return None


# In[5]:


def test_openai():
    openai_client = OpenAIClient()
    response = openai_client.get_response('Hello, world!')
    print(response)


# In[6]:


test_openai()


# In[7]:


get_ipython().system('pip install requests')


# In[8]:


import requests
import os

class HomeAssistantClient:
    def __init__(self):
        self.url = os.environ['HA_SERVER']
        self.headers = {
            "Authorization": f"Bearer {os.environ['HA_TOKEN']}",
            "Content-Type": "application/json"
        }

    def get_state(self, entity_id):
        try:
            response = requests.get(
                f"{self.url}/api/states/{entity_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in getting state: {str(e)}")
            return None

    def set_state(self, entity_id, state):
        try:
            response = requests.post(
                f"{self.url}/api/states/{entity_id}",
                headers=self.headers,
                json={"state": state},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in setting state: {str(e)}")
            
    def get_all_states(self):
        try:
            response = requests.get(
                f"{self.url}/api/states",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in getting all states: {str(e)}")
            return None


# In[9]:


def test_homeassistant():
    ha_client = HomeAssistantClient()
    state = ha_client.get_state('light.Entry')
    print(state)

test_homeassistant()


# In[10]:


get_ipython().system('pip install influxdb-client')


# In[11]:


def list_HA_entities():
    ha_client = HomeAssistantClient()
    entities = ha_client.get_all_states()
    for entity in entities:
        print(entity['entity_id'])

list_HA_entities()


# In[12]:


from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.flux_table import FluxTable
import pandas as pd

class InfluxDBConnection:
    def __init__(self):
        self.client = InfluxDBClient(
            url=os.environ['INFLUX_SERVER'],
            token=os.environ['INFLUX_TOKEN'],
            org=os.environ['INFLUX_ORG']
        )

    def query(self, query):
        try:
            tables = self.client.query_api().query(query, org=self.client.org)
            result = []
            for table in tables:
                for record in table.records:
                    result.append(record.values)
            return result
        except Exception as e:
            print(f"Error in query: {str(e)}")
            return None

    def query_df(self, query):
        try:
            df = self.client.query_api().query_data_frame(query, org=self.client.org)
            return df
        except Exception as e:
            print(f"Error in query: {str(e)}")
            return None

    def write(self, bucket, record):
        try:
            write_api = self.client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket, self.client.org, record)
            write_api.__del__()
        except Exception as e:
            print(f"Error in write: {str(e)}")

    def get_health(self):
        return self.client.health()

    def close(self):
        self.client.__del__()



# In[14]:


def test_influxdb_connection():
    # Instantiate the InfluxDBConnection
    influx_conn = InfluxDBConnection()

    # Test query()
    query = f'from(bucket: "{os.environ["INFLUX_HA_BUCKET"]}")|> range(start: -1h)|> filter(fn: (r) => r["_measurement"] == "temperature")'
    result = influx_conn.query(query)
    print(result)

    # Test query_df()
    result_df = influx_conn.query_df(query)
    print(result_df)

    # Test write()
    # Assuming you have a Point or a list of Points to write
    #points = [Point("measurement").tag("location", "west").field("temperature", 20.3)]
    #bucket = '<Your bucket here>'
    #influx_conn.write(bucket, points)

    # Test get_health()
    health = influx_conn.get_health()
    print(health)

    # Close the connection
    influx_conn.close()

test_influxdb_connection()


# In[15]:


query = f'''
import "influxdata/influxdb/schema"
schema.measurements(bucket: "{os.environ['INFLUX_HA_BUCKET']}")
'''
influx = InfluxDBConnection()
df = influx.query_df(query)
print(df)


# In[17]:


query = f'''
from(bucket: "{os.environ['INFLUX_HA_BUCKET']}")
  |> range(start: -1d)
  |> filter(fn: (r) => r["_measurement"] == "weather.my_ecobee3")
'''
df = influx.query_df(query)
print(df)


# In[ ]:




