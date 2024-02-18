from typing import List

import runhouse as rh


def np_array(num_list: List[int]):
    import numpy as np

    return np.array(num_list)


sm_cluster = (
    rh.sagemaker_cluster(
        name="rh-sagemaker",
        role="arn:aws:iam::172657097474:role/service-role/AmazonSageMaker-ExecutionRole-20230717T192142",
    )
    .up_if_not()
    .save()
)

assert sm_cluster.is_up()

# Run func on the cluster
np_func = rh.function(np_array).to(sm_cluster, env=["./", "numpy"])
my_list = [1, 2, 3]
res = np_func(my_list)
assert res.tolist() == my_list

# Use cluster object store
test_list = list(range(5, 50, 2)) + ["a string"]
sm_cluster.put("my_list", test_list)
ret = sm_cluster.get("my_list")
assert ret == test_list

# Run CLI commands
return_codes = sm_cluster.run(commands=["ls -la"])
assert return_codes[0][0] == 0