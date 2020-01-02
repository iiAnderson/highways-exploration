from metaflow import Flow, get_metadata
print("Current metadata provider: %s" % get_metadata())

run = Flow('HeatMapTimeByTotalTrafficFlow').latest_successful_run
print("Using run: %s" % str(run))

for self_result in run.data.processing_results:
    vals = [0 for x in range(0, len(self_result['data'][0]))]
    for row in self_result['data']:
        for i in range(0, len(row)):
            vals[i] = vals[i] + float(row[i])
    
    for i in range(0, len(vals)):
        vals[i] = vals[i] / len(self_result['data'])


    df = pd.DataFrame([vals])
    df.columns = self_result['x_axis']
    
    df.to_csv(f"csv_out/heat_map/{self_result['name']}-out.csv")

'''
    df = pd.DataFrame(self_result["data"])
    df.columns = self_result['x_axis']
    df.insert(0, column='Time', value=self_result['y_axis'])

    
    df.to_csv(f"csv_out/heat_map_junc_change/{self_result['name']}-out.csv")
'''