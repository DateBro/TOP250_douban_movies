class DefaultConfig(object):
    env = 'default'
    model = 'LSTM'

    train_data_root = './data/train'
    test_data_root = './data/test'
    load_model_path = 'checkpoints/model.pth'

    batch_size = 128
    use_gpu = True

    result_file = 'result.csv'

    max_epoch = 10
    lr = 0.1
    lr_decay = 0.95
    weight_decay = 1e-4

    def parse(self, kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                warnings.warn("Warning: opt not have attribute %s" %k)
            setarrt(self, k, v)

        print('user config')
        for k, v in self.__class__.__dict__.items():
            if not k.startwith('__'):
                print(k, getattr(self, k))