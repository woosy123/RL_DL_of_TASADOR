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
# 한 그룹당 quota sweep 포인트 개수는 고정이 아닐 수 있으니, 이 값은
# "dataset 생성 가정"에만 필요할 때 사용. (현재 tasador_dataset.py는 group split이라 크게 의존 안 함)
TOTAL_NUM_CONFIGS = 0  # 미사용/더미 (필요하면 그룹당 quota 포인트로 설정)

# query feature 길이 = len(used_features) = 9
NUM_CONFIG_PARAMS = 9

# shot feature 길이 = len(used_features) + quota = 9 + 1 = 10
NUM_FEATURES_PER_SHOT = 10

# SNAIL forward에서 query에 대해 'config만' 붙이도록
FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT = False
