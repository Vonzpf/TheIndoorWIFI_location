# -*- coding:utf-8 -*-

# @Author zpf

import random
import numpy as np
import xgboost as xgb


class WIFI_Location:
    def __init__(self, shop_file, user_shop_file, eva_file):
        self.shop_file_addr = shop_file
        self.user_shop_file_addr = user_shop_file
        self.eva_file_addr = eva_file
        # 所有商场id集合:  self.all_mall = {mall_id: [shop_id, ...], ...}
        # 所有商店id集合:  self.all_shop = {shop_id: [category, LONG, LAT, price, mall_id], ...}
        self.all_mall = {}
        self.all_shop = {}
        self.tran_a_data = []
        self.tran_b_data = []
        self.negative_sample = []

        self.data_process(shop_file=self.shop_file_addr,
                          user_shop_file=self.user_shop_file_addr,
                          eva_file=self.eva_file_addr)

    # 转换shop_info.csv中每条记录格式：string－>int或float
    def type_tran_a(self, s_list):
        temp = s_list[0]
        self.tran_a_data[0] = int(temp.split('_')[-1])

        temp = s_list[1]
        self.tran_a_data[1] = int(temp.split('_')[-1])

        self.tran_a_data[2] = float(s_list[2])

        self.tran_a_data[3] = float(s_list[3])

        self.tran_a_data[4] = int(s_list[4])

        temp = s_list[5]
        self.tran_a_data[5] = int(temp.split('_')[-1])
        return self.tran_a_data

    # 转换user_shop_behavior.csv中每条记录格式：string－>int或float
    @staticmethod
    def type_tran_b(s_list):
        # new_list = [shop_id, user_id, LONG, LAT, #date, time,
        #               wifi_id, wifi_power, wifi_id, wifi_power, wifi_id, wifi_power]
        new_list = []

        temp = s_list[1]
        new_list.append(int(temp.split('_')[-1]))

        temp = s_list[0]
        new_list.append(int(temp.split('_')[-1]))

        new_list.append(float(s_list[3]))

        new_list.append(float(s_list[4]))

        # date_time = s_list[2].split(' ')[0].split('-')
        hm_time = s_list[2].split(' ')[1].split(':')
        temp_time = int(hm_time[0]) * 60 + int(hm_time[1])
        new_list.append(temp_time)

        # 优先考虑连上的wifi，并将其放在第一个，筛选出强度最强的三个wifi作为特征，不足补0
        if len(s_list[5].split('|')) < 4:
            temp_wifi = s_list[5].split('|')

            new_list.append(int(temp_wifi[0].split('_')[1]))
            new_list.append(abs(int(temp_wifi[1])))

            new_list.append(0)
            new_list.append(0)

            new_list.append(0)
            new_list.append(0)

        elif len(s_list[5].split('|')) < 6:
            temp_wifi = s_list[5].split(';')
            wifi_a = temp_wifi[0].split('|')
            wifi_b = temp_wifi[1].split('|')
            if wifi_a[2] == 'true':
                new_list.append(int(wifi_a[0].split('_')[1]))
                new_list.append(abs(int(wifi_a[1])))

                new_list.append(int(wifi_b[0].split('_')[1]))
                new_list.append(abs(int(wifi_b[1])))

                new_list.append(0)
                new_list.append(0)
            elif wifi_b[2] == 'true':
                new_list.append(int(wifi_b[0].split('_')[1]))
                new_list.append(abs(int(wifi_b[1])))

                new_list.append(int(wifi_a[0].split('_')[1]))
                new_list.append(abs(int(wifi_a[1])))

                new_list.append(0)
                new_list.append(0)
            else:
                if int(wifi_a[1]) > int(wifi_b[1]):
                    new_list.append(int(wifi_a[0].split('_')[1]))
                    new_list.append(abs(int(wifi_a[1])))

                    new_list.append(int(wifi_b[0].split('_')[1]))
                    new_list.append(abs(int(wifi_b[1])))

                    new_list.append(0)
                    new_list.append(0)
                else:
                    new_list.append(int(wifi_b[0].split('_')[1]))
                    new_list.append(abs(int(wifi_b[1])))

                    new_list.append(int(wifi_a[0].split('_')[1]))
                    new_list.append(abs(int(wifi_a[1])))

                    new_list.append(0)
                    new_list.append(0)

        else:
            temp_wifi = s_list[5].split(';')
            temp_list = []
            order_list = []
            wifi_num = len(temp_wifi)

            # 判断是否有正在连接的wifi
            j = 0
            while j < wifi_num:
                single_wifi = temp_wifi[j].split('|')
                if single_wifi[2] == 'true':
                    temp_list.append(int(single_wifi[0].split('_')[1]))
                    temp_list.append(abs(int(single_wifi[1])))
                    del temp_wifi[j]
                    wifi_num -= 1
                j += 1
            # 将剩下的wifi按照强度排序
            for element in temp_wifi:
                order_list.append(int(element.split('|')[1]))
            order_list.sort()

            while len(temp_list) < 6:
                signal_power = order_list[-1]
                k = 0
                while k < wifi_num:
                    single_wifi = temp_wifi[k].split('|')
                    if int(single_wifi[1]) == signal_power:
                        temp_list.append(int(single_wifi[0].split('_')[1]))
                        temp_list.append(abs(int(single_wifi[1])))
                        del temp_wifi[k]
                        wifi_num -= 1
                        break
                    k += 1
                del order_list[-1]

            for element in temp_list:
                new_list.append(element)

        return new_list

    # 根据传入的正样本生成1个负样本
    def create_negative_sample(self, positive_sample):
        # 所有商场id集合:  self.all_mall = {mall_id: [shop_id, ...], ...}
        # 所有商店id集合:  self.all_shop = {shop_id: [category, LONG, LAT, price, mall_id], ...}

        # positive_sample = [shop_id, user_id, LONG, LAT, #date, time,
        #                    wifi_id, wifi_power, wifi_id, wifi_power, wifi_id, wifi_power]
        shop_id = positive_sample[0]
        shop_info_value = self.all_shop[shop_id]
        # shop_category = shop_info_value[0]
        mall_id = shop_info_value[-1]
        shop_belong_to_mall = self.all_mall[mall_id]

        # # 计算距离度量最近的两个商店
        # min_distance = 10000
        # for each_shop in shop_belong_to_mall:
        #     each_shop_info_value = self.all_shop[each_shop]
        #     distance = each_shop_info_value[1] - positive_sample[2] + each_shop_info_value[2] - positive_sample[3]
        #     if distance < min_distance:
        #         min_distance = distance
        #         negative_sample = each_shop_info_value[0]

        # 随机选取同商场的一个其他shop作为负样本
        shop_selected = shop_id
        seed = list(range(len(shop_belong_to_mall)))
        while shop_selected == shop_id:
            random.shuffle(seed)
            shop_selected = shop_belong_to_mall[seed[0]]
        self.negative_sample = positive_sample.copy()
        self.negative_sample[0] = shop_selected

        return self.negative_sample

    def data_process(self, shop_file, user_shop_file, eva_file):
        # 读取shop_info数据文件，并建立商场、商店的查找字典
        shop_data = np.loadtxt(shop_file, delimiter=",", skiprows=1, dtype=np.string_)
        shop_data = shop_data.astype(np.str)

        for element in shop_data:
            temp = []
            element = list(element)
            element = self.type_tran_a(element)

            if element[-1] in self.all_mall:
                self.all_mall[element[-1]].append(element[0])
            else:
                temp.append(element[0])
                self.all_mall[element[-1]] = temp

            # element[1:] = [category, LONG, LAT, price, mall_id]
            self.all_shop[element[0]] = element[1:]
            # print(self.all_shop)

        # 读取user_shop_behavior数据文件，并建立训练数据文件
        user_shop_data = np.loadtxt(user_shop_file, delimiter=",", skiprows=1, dtype=np.string_)
        user_shop_data = user_shop_data.astype(np.str)

        train_data = np.array([])
        for element in user_shop_data:
            temp = []
            temp.append(element)
            element = list(element)
            element = self.type_tran_b(element)
            # element = [shop_id, user_id, LONG, LAT, #date, time,
            #               wifi_id, wifi_power, wifi_id, wifi_power, wifi_id, wifi_power]

            # 对每条记录生成负样本
            negative_example = self.create_negative_sample(element)
            temp.append(negative_example)

            if train_data == np.array([]):
                train_data = np.array(temp)
            else:
                print(train_data.shape)
                print(np.array(temp).shape)
                train_data = np.vstack((train_data, np.array(temp)))
        np.savetxt("./data/train_data.txt")

if __name__ == "__main__":
    shop_info = "./data/shop_info.csv"
    user_shop_behavior = "./data/user_shop_behavior.csv"
    evaluation_public = "./data/evaluation_public"
    X = WIFI_Location(shop_info, user_shop_behavior, evaluation_public)
