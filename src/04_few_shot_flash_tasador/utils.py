from torch.utils.data.sampler import SubsetRandomSampler
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from tasador_dataset import TasadorDatasetXSamplesDifferentAppsForTrainTestValidate

def init_dataset(opt, validation_only=False):
    '''
    Initialize the datasets, samplers and dataloaders
    '''
    if opt.dataset == 'tasador':
        data_root = getattr(opt, 'data_root', '.')
        train_csv = getattr(opt, 'train_csv', 'tasador_dataset.csv')
        test_csv  = getattr(opt, 'test_csv',  'tasador_config2.csv')

        support_strategy = getattr(opt, 'support_strategy', 'uniform')
        query_strategy = getattr(opt, 'query_strategy', 'uniform')
        max_queries_per_group = getattr(opt, 'max_queries_per_group', None)

        if validation_only:
            val_dataset = TasadorDatasetXSamplesDifferentAppsForTrainTestValidate(
                num_samples=opt.num_shots,
                mode='test',
                root=data_root,
                train_filename=train_csv,
                test_filename=test_csv,
                normalize_x=True,
                support_strategy=support_strategy,
                query_strategy=query_strategy,
                max_queries_per_group=max_queries_per_group,
            )
            trainval_dataloader = DataLoader(
                val_dataset,
                batch_size=opt.batch_size,
                sampler=SubsetRandomSampler(list(range(len(val_dataset)))),
                num_workers=0,
                drop_last=False
            )
            return trainval_dataloader

        train_dataset = TasadorDatasetXSamplesDifferentAppsForTrainTestValidate(
            num_samples=opt.num_shots,
            mode='train',
            root=data_root,
            train_filename=train_csv,
            test_filename=test_csv,
            normalize_x=True,
            support_strategy=support_strategy,
            query_strategy=query_strategy,
            max_queries_per_group=max_queries_per_group,
        )

        test_dataset = TasadorDatasetXSamplesDifferentAppsForTrainTestValidate(
            num_samples=opt.num_shots,
            mode='test',
            root=data_root,
            train_filename=train_csv,
            test_filename=test_csv,
            normalize_x=True,
            support_strategy=support_strategy,
            query_strategy=query_strategy,
            max_queries_per_group=max_queries_per_group,
        )

        all_train_idx = list(range(len(train_dataset)))
        train_idx, val_idx = train_test_split(
            all_train_idx, test_size=0.2, random_state=42, shuffle=True
        )

        tr_dataloader = DataLoader(
            train_dataset,
            batch_size=opt.batch_size,
            sampler=SubsetRandomSampler(train_idx),
            num_workers=0,
            drop_last=False
        )

        val_dataloader = DataLoader(
            train_dataset,
            batch_size=opt.batch_size,
            sampler=SubsetRandomSampler(val_idx),
            num_workers=0,
            drop_last=False
        )

        test_dataloader = DataLoader(
            test_dataset,
            batch_size=opt.batch_size,
            sampler=SubsetRandomSampler(list(range(len(test_dataset)))),
            num_workers=0,
            drop_last=False
        )

        return tr_dataloader, val_dataloader, test_dataloader, None

    else:
        raise ValueError('Not recognized task!')