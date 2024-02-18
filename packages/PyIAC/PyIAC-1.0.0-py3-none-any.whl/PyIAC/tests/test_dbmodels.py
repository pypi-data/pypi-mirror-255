import unittest
from PyIAC.dbmodels import Units, Variables, DataTypes, Tags, AlarmsDB
from PyIAC.dbmodels import AlarmTypes, AlarmPriorities, AlarmStates
from PyIAC.alarms import Alarm


class TestDBModels(unittest.TestCase):
    r"""
    Documentation here
    """

    def setUp(self) -> None:


        self.__tags = [
            ('PT-01', 'Pa', 'float', 'Inlet Pressure', 'PT-01'),
            ('PT-02', 'Pa', 'float', 'Outlet Pressure', 'PT-02'),
            ('FT-01', 'kg/s', 'float', 'Inlet Mass Flow', 'FT-01'),
            ('FT-02', 'kg/s', 'float', 'Outlet Mass Flow', 'FT-02')
        ]

        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()

    def testCountVariablesAdded(self):

        result = Variables.read_all()

        self.assertEqual(len(result), 20)

    def testCountUnitsAdded(self):

        result = Units.read_all()

        self.assertEqual(len(result), 145)

    def testCountDataTypesAdded(self):

        result = DataTypes.read_all()

        self.assertEqual(len(result), 4)

    def testCountAlarmPrioritiesAdded(self):

        result = AlarmPriorities.read_all()

        self.assertEqual(len(result), 6)

    def testCountAlarmTypesAdded(self):

        result = AlarmTypes.read_all()

        self.assertEqual(len(result), 6)

    def testCountAlarmStatesAdded(self):

        result = AlarmStates.read_all()

        self.assertEqual(len(result), 7)

    def testDefineAlarm(self):
        r"""
        Documentation here
        """
        for name, unit, data_type, description, display_name in self.__tags:

            Tags.create(
                name=name,  
                unit=unit, 
                data_type=data_type,
                description=description,
                display_name=display_name)

        alarm_name, tag, description, alarm_type, alarm_trigger = (
            "alarm_PT_01", 
            "PT-01", 
            "Ejemplo High-High",
            "HIGH-HIGH",
            55.5
        )

        alarm = Alarm(name=alarm_name, tag=tag, description=description)
        alarm.set_trigger(value=alarm_trigger, _type=alarm_type)
        _alarm = AlarmsDB.read_by_name(name=alarm_name)
        _alarm_result = _alarm.serialize()
        _alarm_result.pop('id')

        expected_result = {
            'name': alarm_name, 
            'tag': tag, 
            'description': description, 
            'alarm_type': alarm_type, 
            'trigger': alarm_trigger
        }

        self.assertEqual(_alarm_result, expected_result)
