import json

import bw2data

from enbios.base.experiment import Experiment

PROJECT_NAME = "ecoinvent_391"
DATABASE = "ecoinvent_391_cutoff"

bw2data.projects.set_current(PROJECT_NAME)
db = bw2data.Database(DATABASE)

#


wind_turbines_spain = db.search(
    "electricity production, wind, 1-3MW turbine, onshore", filter={"location": "ES"}
)[:2]

# for the experiment we need to create a list of activities (or a dict, where the keys represent the aliases)
# We need to add the codes, otherwise the brightway search will not be not uniquely identify the activities
# adding name is just for convenience
experiment_hierarchy = {"name": "root", "aggregator": "sum", "children": []}

for activity in wind_turbines_spain[:2]:
    experiment_hierarchy["children"].append(
        {
            "name": activity["name"],
            "id": {"name": activity["name"], "code": activity["code"]},
            "adapter": "bw",
            "output": ["kilowatt_hour", 10],
        }
    )

# select 2 random methods and convert them into the form for enbios2
# methods = [bw2data.methods.random() for _ in range(2)]
# experiment_methods = [{"id": method} for method in methods]
experiment_methods = {
    "GWP1000": {
        "id": (
            "ReCiPe 2016 v1.03, midpoint (H)",
            "climate change",
            "global warming potential (GWP1000)",
        )
    }
    # "FETP": {
    #     "id": (
    #         "ReCiPe 2016 v1.03, midpoint (H)",
    #         "ecotoxicity: freshwater",
    #         "freshwater ecotoxicity potential (FETP)",
    #     )
    # },
}

# let's store the raw data, because we want to modify it later
simple_raw_data = {
    "hierarchy": experiment_hierarchy,
    "adapters": [
        {
            "module_path": "/home/ra/projects/enbios/enbios/bw2/brightway_experiment_adapter.py",
            "config": {"bw_project": "ecoinvent_391"},
            "methods": experiment_methods,
        },
        {
            "module_path": "/home/ra/projects/enbios/enbios/demos/DemoAdapter.py",
        },
    ],
}

# make a first validation of the experiment data
# exp_data = ExperimentData(**simple_raw_data)
# simple_experiment: Experiment = Experiment(simple_raw_data)

# for scenario in simple_experiment.scenarios:
#     print(json.dumps(scenario.run(), indent=2))
#     print("---")


experiment_hierarchy["children"].append(
    {
        "name": "some activity",
        "adapter": "demo-adapter",
        "id": "some activity",
        "output": ["megawatt_hour", 10],
    }
)

simple_raw_data["scenarios"] = [
    {"name": "scenario 1"},
    {
        "name": "scenario XX",
        "activities": {
            "electricity production, wind, 1-3MW turbine, onshore": ["kilowatt_hour", 15],
            "some activity": ["megawatt_hour", 20],
        },
    },
]

simple_experiment2: Experiment = Experiment(simple_raw_data)

# for scenario in simple_experiment2.scenarios:
#     print(scenario.describe())
#     print(json.dumps(scenario.run(), indent=2))
#     print("---")

# print(json.dumps(simple_experiment2.run_scenario_config({"name": "scenario XX",
#                                                          "config": {"exclude_defaults": True},
#                                                          "activities": {
#                                                              "electricity production, wind, 1-3MW turbine, onshore": [
#                                                                  "kilowatt_hour", 15],
#                                                              "some activity": ["megawatt_hour", 20]}}), indent=2))


experiment_hierarchy["children"].append(
    {
        "name": "some aggregator",
        "aggregator": "sum",
        "children": [
            {
                "name": "some activity2",
                "adapter": "demo-adapter",
                "id": "some activityX",
                "output": ["megawatt_hour", 10],
            }
        ],
    }
)
# print(json.dumps(experiment_hierarchy, indent=2))

simple_experiment2: Experiment = Experiment(simple_raw_data)

print(
    json.dumps(
        simple_experiment2.run_scenario_config(
            {
                "name": "scenario XX",
                "config": {"exclude_defaults": True},
                "activities": {
                    "electricity production, wind, 1-3MW turbine, onshore": [
                        "kilowatt_hour",
                        15,
                    ],
                    "some activity": ["megawatt_hour", 20],
                },
            }
        ),
        indent=2,
    )
)
