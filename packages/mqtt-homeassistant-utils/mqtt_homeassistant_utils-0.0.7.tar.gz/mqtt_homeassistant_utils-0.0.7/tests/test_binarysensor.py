import unittest
import json

from mqtt_homeassistant_utils.binarysensor import HABinarySensor

class TestBinarySensor(unittest.TestCase):
    def test_mandatory_attributes(self):
        MQTT_TOPIC = "test"

        testBinarySensor = HABinarySensor(
            state_topic=MQTT_TOPIC + "/values",
            name="MyTestSensor",
            node_id=MQTT_TOPIC,
            unique_id=MQTT_TOPIC + "_uid"
        )

        testJson = testBinarySensor.to_json()

        #convert into dict
        testDict = json.loads(testJson)

        #check for attributes
        self.assertIn("state_topic", testDict)
        self.assertEqual(testDict["state_topic"], MQTT_TOPIC + "/values")

        self.assertIn("name", testDict)
        self.assertEqual(testDict["name"], "MyTestSensor")

        self.assertIn("node_id", testDict)
        self.assertEqual(testDict["node_id"], MQTT_TOPIC)

        self.assertIn("uniqued_id", testDict)
        self.assertEqual(testDict["unique_id"], MQTT_TOPIC + "_uid")

        



if __name__ == '__main__':
    unittest.main()    