import handler
import sys

def local_invoke_lambda_handler(task_id):
    event = {
          "config": "load_input_path: /mnt/efs/criteo_kaggle/train.csv \nload_input_type: csv\ndataset_format: binary\nnum_classes: 2 \nnum_features: 13 \nlimit_cols: 14 \nnormalize: 0 \nlimit_samples: 10000 \ns3_size: 50000 \nuse_bias: 1 \nmodel_type: LogisticRegression \nminibatch_size: 200 \nlearning_rate: 0.000100 \nepsilon: 0.000100 \nmodel_bits: 19 \ns3_bucket: criteo-kaggle-19b \nuse_grad_threshold: 0 \ngrad_threshold: 0.001000 \ntrain_set: 0-799 \ntest_set: 800-850",
          "num_workers": 16,
          "ps_ip": "128.84.139.16",
          "ps_port": 1337,
          "task_id": task_id,
          "log_level": "DEBUG"
        }
    handler.run(event, None, local=True)

if __name__ == "__main__":
    local_invoke_lambda_handler(int(sys.argv[1]))
