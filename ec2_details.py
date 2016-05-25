from core import CoreProcessor
from datetime import datetime


def create_sheet(json_string, csv_filename='ec2_details.csv'):
    processor = EC2DetailsProcessor(json_string)
    return processor.write_csv(csv_filename)


class EC2DetailsProcessor(CoreProcessor):
    def __data_key__(self):
        return 'Ec2Instances'

    def __filter_row__(self, details_row):
        filtered_row = {
            key: details_row[key] for key in self.__fieldnames__() if key in details_row.keys()
        }

        return self.__format_datefields__(filtered_row)

    def __format_datefields__(self, row):
        for datefields in self.__datetime_fields__():
            row[datefields] = datetime.strptime(
                row[datefields], '%Y-%m-%dT%H:%M:%S'
            ).strftime('%m/%d/%y %H:%M')

        return row

    def __fieldnames__(self):
        return [
            'InstanceId', 'InstanceName', 'Status', 'Region', 'PricingPlatform',
            'InstanceType', 'LaunchTime', 'AvgCpuforLast7Days', 'AvgCpuforLast30Days',
            'AvgCpuforLast90Days', 'AvgNetworkInLast30Days', 'AvgNetworkOutLast30Days',
            'HighCpuPercent', 'LowCpuPercent', 'HoursCpuUtilAbove80', 'HoursCpuUtilBelow80',
            'HoursCpuUtilBelow60', 'HoursCpuUtilBelow40', 'HoursCpuUtilBelow20',
            'HoursHighCpuLast7Days', 'HoursHighCpuLast30Days', 'HoursHighCpuLast90Days',
            'HoursLowCpuLast7Days', 'HoursLowCpuLast30Days', 'HoursRunningLast7Days',
            'HoursRunningLast30Days', 'HoursRunningLast90Days', 'MinimumCpuUtilization',
            'MinimumCpuUtilizationDateTime', 'PeakCpuUtilization', 'PeakCpuUtilizationDateTime'
        ]

    def __datetime_fields__(self):
        return [
            'MinimumCpuUtilizationDateTime', 'PeakCpuUtilizationDateTime', 'LaunchTime'
        ]