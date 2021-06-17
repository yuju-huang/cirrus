import sys
import re
import matplotlib.pyplot as plt
import numpy as np
import statistics
from scipy.interpolate import interp1d

# Latency data for each percentile
class LatencyData:
    def __init__(self, qps, percentile):
        self.qps = qps
        self.percentile = percentile
        self.data = []

    def add(self, lat):
        assert (lat.find("us") == -1)
        find_ms = lat.find("ms")
        if find_ms != -1:
            self.data.append(float(lat[:find_ms]))
        else:
            self.data.append(1000 * float(lat[:lat.find("s")]))

    def get_average(self):
        return sum(self.data) / len(self.data)

    def dump(self):
        print("qps=" + str(self.qps) + ", percentile=" + str(self.percentile) + ", avg=" + str(self.get_average()))

# Final result for each QPS
class Result:
    def __init__(self):
        # Map from percentile to {qps to LatencyData}
        # For example, {99% -> {{qps=1000 -> LatencyData}, {qps=2000 -> LatencyData}}
        self.latency_data = {}

    def add(self, q, p, lat):
        percentile = float(p[:p.find('%')])
        qps = int(q)
        assert (qps > 0)
        assert (percentile > 0)
        if (percentile not in self.latency_data):
            self.latency_data[percentile] = {}

        self.add_to_percentile(self.latency_data[percentile], qps, percentile, lat)

    def add_to_percentile(self, d, qps, percentile, lat):
        if (qps in d):
            d[qps].add(lat)
        else:
            data = LatencyData(qps, percentile)
            data.add(lat)
            d[qps] = data

    def draw(self, interpolate=False, log_scale=False):
        # k is percentile 
        for k in sorted(self.latency_data.keys()):
            print("percentile=" + str(k))
            data = []
            for k2 in sorted(self.latency_data[k].keys()):
                data.append(self.latency_data[k][k2].get_average())
            x = list(list(self.latency_data.values())[0].keys())
            if interpolate == False:
                plt.plot(x, data, label=(str(k) + "%"))
            else:
                # Cubic interpolation
                y_cubic = interp1d(x, data, kind='cubic')
                x_new = np.linspace(x[0], x[-1], num=100, endpoint=True)
                plt.plot(x_new, y_cubic(x_new), label=(str(k) + "%"))

        if (log_scale):
            plt.yscale('log')
        plt.xlabel('QPS')
        plt.ylabel('Latency (ms)')
        plt.legend(loc='best')
        plt.show()

    def dump(self):
        # k is percentile 
        for k in sorted(self.latency_data.keys()):
            print("percentile=" + str(k))
            for k2 in sorted(self.latency_data[k].keys()):
                self.latency_data[k][k2].dump()

"""
    def add(self, q, percentile, lat):
        qps = int(q)
        assert (qps > 0)
        if (qps not in self.latency_data):
            self.latency_data[qps] = {}

        self.add_to_percentile(self.latency_data[qps], percentile, lat)

    def add_to_percentile(self, d, percentile, lat):
        if (percentile in d):
            d[percentile].add(lat)
        else:
            data = LatencyData(percentile)
            data.add(lat)
            d[percentile] = data

    def dump(self):
        self.latency_data = sorted(self.latency_data.items())
        print(self.latency_data)

        # k is qps 
        for k, v in sorted(self.latency_data):
            print("qps=" + str(k))
            for v2 in v.values():
                v2.dump()
"""

"""
/aws/lambda/cirrus_worker_0_2021-6-15_18-20-36-650089 2021/06/15/[$LATEST]073e396d3c424b4992ccbad99a3b03c6 [WORKER] Get dataset elapsed (us): 2060665
/aws/lambda/cirrus_worker_0_2021-6-15_18-20-36-650089 2021/06/15/[$LATEST]073e396d3c424b4992ccbad99a3b03c6 [WORKER] Get model elapsed (us): 4949
/aws/lambda/cirrus_worker_0_2021-6-15_18-20-36-650089 2021/06/15/[$LATEST]073e396d3c424b4992ccbad99a3b03c6 [WORKER] Compute gradient elapsed (us): 96200
/aws/lambda/cirrus_worker_0_2021-6-15_18-20-36-650089 2021/06/15/[$LATEST]073e396d3c424b4992ccbad99a3b03c6 [WORKER] Sent gradient elapsed (us): 18706
"""
result = Result()
if __name__ == "__main__":
    get_dataset = []
    get_model = []
    compute_gradient = []
    push_gradient = []

    with open(sys.argv[1]) as f:
        line = f.readline()
        qps = -1
        while line:
            line = line.strip()
            l = line.split()
            if (line.find("Get dataset") != -1):
                get_dataset.append(int(l[-1]))
            elif (line.find("Get model") != -1):
                get_model.append(int(l[-1]))
            elif (line.find("Compute gradient") != -1):
                compute_gradient.append(int(l[-1]))
            elif (line.find("Sent gradient") != -1):
                push_gradient.append(int(l[-1]))
            
            line = f.readline()

    get_dataset_mean = statistics.mean(get_dataset)
    get_model_mean = statistics.mean(get_model)
    compute_gradient_mean = statistics.mean(compute_gradient)
    push_gradient_mean = statistics.mean(push_gradient)

    get_dataset_std = statistics.stdev(get_dataset)
    get_model_std = statistics.stdev(get_model)
    compute_gradient_std = statistics.stdev(compute_gradient)
    push_gradient_std = statistics.stdev(push_gradient)

    print("get_dataset_mean=", get_dataset_mean)
    print("get_model_mean=", get_model_mean)
    print("compute_gradient_mean=", compute_gradient_mean)
    print("push_gradient_mean=", push_gradient_mean)

    print("get_dataset_std=", get_dataset_std)
    print("get_model_std=", get_model_std)
    print("compute_gradient_std=", compute_gradient_std)
    print("push_gradient_std=", push_gradient_std)

    x = list(range(1, len(get_dataset) + 1))
    plt.plot(x, get_dataset, label=("Get dataset"))
    plt.plot(x, get_model, label=("Get model"))
    plt.plot(x, compute_gradient, label=("Compute gradient"))
    plt.plot(x, push_gradient, label=("Push gradient"))

    plt.xlabel('Sample point')
    plt.ylabel('Time (us)')
    plt.legend(loc='best')
    plt.show()
