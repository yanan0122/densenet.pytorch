import os
import pickle


class Data_handler:
    """
    to divide the cifar by class
    """

    def __init__(self, data_dir):
        # assert os.path.exists(data_dir), "Data_dir is wrong!"
        self.data_dir_path = data_dir
        train_list = os.listdir(self.data_dir_path)
        self.train_list = []
        for file_name in train_list:
            if "data" in file_name:
                self.train_list.append(file_name)
        self.data = []
        for i in range(10):
            # lis = []
            dic = {"data": [],
                   "labels": [],
                   "filenames": []
                   }
            # lis.append(dic)
            self.data.append(dic)

    def divide_by_class(self, target_dir) -> None:
        for file_name in self.train_list:
            file_path = os.path.join(self.data_dir_path, file_name)
            self.handle_one_batch(file_path)
        os.mkdir(target_dir)
        for i in range(10):
            new_file_name = f"data_class_{i}"
            new_file_path = os.path.join(target_dir, new_file_name)
            f_save = open(new_file_path, "wb")
            pickle.dump(self.data[i], f_save)
            f_save.close()

    def handle_one_batch(self, file_path) -> None:
        with open(file_path, "rb") as f:
            entry = pickle.load(f, encoding="latin1")
            for i in range(len(entry['labels'])):
                label = entry['labels'][i]
                self.data[label]["data"].append(entry["data"][label])
                self.data[label]["labels"].append(label)
                self.data[label]["filenames"].append(entry['filenames'][label])




if __name__ == '__main__':
    data_hander = Data_handler("../cifar/cifar-10-batches-py")
    # data_hander.handle_one_batch("../cifar/cifar-10-batches-py/data_batch_1")
    data_hander.divide_by_class("../cifar_after_divide")
    print("finish")

