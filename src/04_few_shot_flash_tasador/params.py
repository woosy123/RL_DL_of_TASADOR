# USE_ALL_FEATURES = False

# Sizeless
# TOTAL_NUM_CONFIGS = 6
# NUM_CONFIG_PARAMS = 1  # memory size
# NUM_FEATURES_PER_SHOT = 13  # selected features: 13, all usable features: 81
# FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT = False  # False if only feeding configs to predict to the final NN

# CloudBandit
#TOTAL_NUM_CONFIGS = 64  # each application consists of 64 samples, each under a different config
#NUM_CONFIG_PARAMS = 9  # nodes + config type vector
#NUM_FEATURES_PER_SHOT = 11  # 9 + 2 (cost/runtime)
#FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT = True  # False if only feeding configs to predict to the final NN

# OWK
# TOTAL_NUM_CONFIGS = 36
# NUM_CONFIG_PARAMS = 2  # cpu, memory
# NUM_FEATURES_PER_SHOT = 51  # 51 (all metrics + cpu + memory + duration)
# FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT = True  # False if only feeding configs to predict to the final NN


# TASADOR
TOTAL_NUM_CONFIGS = 0

NUM_CONFIG_PARAMS = 9

NUM_FEATURES_PER_SHOT = 10

FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT = False
