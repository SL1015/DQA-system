from flask import Flask, request, jsonify, Blueprint, current_app
import csv
from werkzeug.utils import secure_filename
import os
import json
from pymongo import MongoClient
import re
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import normalized_mutual_info_score
from scipy.stats import entropy
from sklearn.impute import SimpleImputer
from collections import Counter
import joblib
from io import BytesIO
import xgboost

upload_blueprint = Blueprint('upload', __name__)

@upload_blueprint.route('/upload', methods=['POST'])
def upload_for_assessment():
    
    if 'file'not in request.files or 'labelColumn' not in request.form:
        return jsonify({'error': 'No file or label column provided'}), 400

    file = request.files['file']
    model_file = request.files['modelFile']
    if model_file:
        model_in_memory = BytesIO(model_file.read())
        model = joblib.load(model_in_memory)
    else:
        model = None
         
    label_column = request.form['labelColumn']
    extra_fields_weight = float(request.form.get('extra_fields', 0.5))
    inconsistent_column_weight = float(request.form.get('inconsistent_column'))
    missing_values_ratio_weight = float(request.form.get('missing_values_ratio'))
    duplicate_rows_weight = float(request.form.get('duplicate_rows'))
    duplicate_columns_weight = float(request.form.get('duplicate_columns'))
    outlier_ratio_weight = float(request.form.get('outlier_ratio'))
    class_imbalance_ratio_weight = float(request.form.get('class_imbalance_ratio'))
    label_purity_weight = float(request.form.get('label_purity'))
    constant_features_weight = float(request.form.get('constant_features'))
    feature_relevance_weight = float(request.form.get('feature_relevance'))
    feature_correlation_weight = float(request.form.get('feature_correlation'))
    target_leakage_ratio_weight = float(request.form.get('target_leakage_ratio'))

    pillar_feature_relevance_weight = float(request.form.get('feature_relevance_weight'))
    pillar_uniqueness_weight = float(request.form.get('uniqueness_weight'))
    pillar_consistency_weight = float(request.form.get('consistency_weight'))

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if 'pcap.netflow' in filename:
            with open(file_path, 'r') as file:
                pattern = '[ \t,;]+'
                document = []
                # Read the header line
                line = file.readline().strip()
                headers = re.split(pattern, line)
                print("Headers:", headers)
                
                for line in file:
                    line = line.strip()
                    fields  = re.split(pattern, line)
                    row = {}
                    
                    for index, field in enumerate(fields):
                        if index < len(headers):
                            row[headers[index]] = field
                        else:
                            # Collect extra fields
                            if 'extra_fields' not in row:
                                row['extra_fields'] = []
                            row['extra_fields'].append(field)
                    
                    # If extra fields are collected, join them into a single string
                    if 'extra_fields' in row:
                        row['extra_fields'] = ' '.join(row['extra_fields'])
                        
                    document.append(row)
        
            # Convert the document list to a DataFrame
            df = pd.DataFrame(document)
            print(df.head)
            if label_column not in df.columns:
                return jsonify({'error': f'Label column "{label_column}" not found in dataset'}), 400
            
            # # If 'extra_fields' column exists, drop it
            # if 'extra_fields' in df.columns:
            #     df.drop(columns=['extra_fields'], inplace=True)
        
        else:
            with open(file_path, 'r') as file:
                document = []
                reader = csv.reader(file)
                headers = next(reader)  # 读取文件的第一行作为标题
                print("Headers:", headers)
        
                for line in reader:
                    row = {}
                    for index, field in enumerate(line):
                        if index < len(headers):
                            if field == '':  # 处理空字符串为NaN
                                row[headers[index]] = np.nan
                            else:
                                row[headers[index]] = field
                        else:
                            if 'extra_fields' not in row:
                                row['extra_fields'] = []
                            row['extra_fields'].append(field)
                    # if 'extra_fields' in row:
                    #     row['extra_fields'] = ' '.join(row['extra_fields'])                   
                    document.append(row)
            # Convert the document list to a DataFrame
            df = pd.DataFrame(document)
            if label_column not in df.columns:
                return jsonify({'error': f'Label column "{label_column}" not found in dataset'}), 400
            # If 'extra_fields' column exists, drop it
            # if 'extra_fields' in df.columns:
            #     df.drop(columns=['extra_fields'], inplace=True)
            print(df.head())

        def cal_metrics(df, label_column):
            metrics = {}
            num_rows = len(df)
            num_cells = df.size
            num_columns = df.shape[1]

            '''----------------------Traditional pillars---------------------'''

            '''--------extra fields (Structual consistency)----------'''
            if 'extra_fields' in df.columns:
                non_null_count = df['extra_fields'].notnull().sum()
                extra_fields_ratio = non_null_count / num_rows
                metrics['extra_fields'] = 1 - extra_fields_ratio
                # Delete the 'extra_fields' column
                df.drop(columns=['extra_fields'], inplace=True)
                print("'extra_fields' has been deleted from the DataFrame.")
            else:
                metrics['extra_fields'] = 1
                print("Column 'extra_field' does not exist in the DataFrame.")

            '''--------Missing Values----------'''
            missing_values_ratio = df.isnull().mean()
            missing_values_ratio_dict = {col: float(ratio) for col, ratio in zip(missing_values_ratio.index, missing_values_ratio.values)}
            average_missing_values_ratio = missing_values_ratio.mean()
            metrics['missing_values_ratio'] = 1 - float(average_missing_values_ratio)

            '''--------Inconsistent column----------'''
            inconsistent_column = 0
            for column in df.columns:
                if df[column].apply(lambda x: isinstance(x, list)).any():
                    print(f"Column '{column}' contains lists. Converting to tuples.")
                    df[column] = df[column].apply(tuple)
                unique_types = df[column].apply(type).unique()
                if len(unique_types) != 1:
                    inconsistent_column += 1
            inconsistent_column_ratio = inconsistent_column / num_columns
            metrics['inconsistent_column'] = 1 - inconsistent_column_ratio

            '''--------duplicate rows----------'''
            duplicate_rows = df.duplicated().sum()
            duplicate_rows_ratio = duplicate_rows / num_rows
            metrics['duplicate_rows'] = 1 - duplicate_rows_ratio

            '''--------duplicate columns----------'''
            duplicate_columns = {}
            columns = df.columns
            for i in range(len(columns)):
                col1 = columns[i]
                for j in range(i + 1, len(columns)):
                    col2 = columns[j]
                    # 判断两个列是否相等
                    if df[col1].equals(df[col2]):
                        if col1 in duplicate_columns:
                            duplicate_columns[col1].append(col2)
                        else:
                            duplicate_columns[col1] = [col2]
            total_duplicate_columns = sum(len(cols) for cols in duplicate_columns.values())
            duplicate_columns_ratio = total_duplicate_columns / num_columns
            metrics['duplicate_columns'] = 1 - duplicate_columns_ratio

            '''--------constant features----------'''
            unique_counts = df.nunique()
            one_unique_value_columns = unique_counts[unique_counts == 1]
            num_one_unique_value_columns = len(one_unique_value_columns)
            constant_feature_ratio = num_one_unique_value_columns / num_columns
            metrics['constant_features'] = 1 - constant_feature_ratio

            '''----------------------AI pillars---------------------'''

            '''--------outlier ratio (Z-score)----------'''
            total_outliers = 0
            total_numeric_entries = 0
            
            # Iterate through each column to determine its type
            for column in df.columns:
                if pd.api.types.is_numeric_dtype(df[column]):
                    # Handle missing values by dropping them
                    valid_data = df[column].dropna()
                    # Calculate Z-scores for numeric columns
                    z_scores = np.abs(stats.zscore(valid_data))
                    outliers = z_scores > 3
                    total_outliers += np.sum(outliers)
                    # Update the total number of numeric entries
                    total_numeric_entries += len(valid_data)
            print(total_numeric_entries)

            if total_numeric_entries > 0:
                outlier_ratio = total_outliers / total_numeric_entries
            else:
                outlier_ratio = 0  # To handle the case where there are no numeric entries
            metrics['outlier_ratio'] = 1 - outlier_ratio
            print("outlier calculated.")

            '''--------label purity----------'''
            # 计算label pattern一致性得分
            df[label_column] = df[label_column].astype(str)
            num_classes = df[label_column].nunique()
            print(num_classes)

            unique_values = df[label_column].unique()
            print("Unique values in the label column:")
            print(unique_values)
            
            def detect_label_type_consistency(df, label_column):
                if df[label_column].apply(lambda x: x.isnumeric()).all():
                    return 1.0
                if df[label_column].apply(lambda x: isinstance(x, str)).all():
                    return 1.0
                return 0.0
            
            def detect_label_pattern_consistency(df, label_column):
                pattern_counts = {}
                num_rows = len(df[label_column])  
                for label in df[label_column]:
                    # detect patterns of label
                    pattern = re.sub(r'[A-Za-z]+', 'A', label)  # 将所有连续字母替换为 'A'
                    pattern = re.sub(r'[0-9]+', '0', pattern)  # 将所有连续数字替换为 '0'
                    
                    if pattern in pattern_counts:
                        pattern_counts[pattern] += 1  # 模式已存在，计数加一
                    else:
                        pattern_counts[pattern] = 1  # 模式不存在，初始化计数为一
                # 计算每种模式的频率
                pattern_frequencies = {pattern: count / num_rows for pattern, count in pattern_counts.items()}
                return pattern_frequencies
            
            def calculate_pattern_consistency_score(df, label_column):
                pattern_frequencies = detect_label_pattern_consistency(df, label_column)
                # 提取频率值
                frequencies = list(pattern_frequencies.values())
                # 计算熵
                pattern_entropy = entropy(frequencies)
                # 归一化熵值到0到1的范围内（假设最大熵为log(模式数量)）
                max_entropy = np.log(len(frequencies)) if frequencies else 1
                normalized_entropy = pattern_entropy / max_entropy if max_entropy > 0 else 0
                # 反转熵值使其成为一致性度量（熵越大，一致性越低）
                consistency_score = 1 - normalized_entropy
                return consistency_score
            
            def calculate_combined_label_consistency_score(df, label_column, pattern_weight=0.5, type_weight=0.5):
                pattern_consistency_score = calculate_pattern_consistency_score(df, label_column)
                type_consistency_score = detect_label_type_consistency(df, label_column)
                combined_consistency_score = pattern_weight * pattern_consistency_score + type_weight * type_consistency_score
                return combined_consistency_score

            label_consistency_score = calculate_combined_label_consistency_score(df, label_column)
            metrics['label_purity'] = label_consistency_score
            print("label purity calculated")
            
            '''--------class imbalance ratio----------'''
            # metric: gini index, the lower the gini index, the more balanced the classes
            df_drop_na_labels = df.dropna(subset=[label_column])
            class_counts = df_drop_na_labels[label_column].value_counts()
            class_probabilities = class_counts / num_rows
            gini_index = 1 - np.sum(class_probabilities ** 2)
            metrics['class_imbalance_ratio'] = 1 - gini_index # gini index itself represents class imbalance ratio
            print("class imbalance calculated")

            '''--------feature importance----------'''
            def cal_mutual_information(df, label_column):
                # metric: mutual information
                X = df.drop(columns=[label_column])
                y = df[label_column]
                print(y[:10])
                label_encoders = {}
                for column in X.select_dtypes(include=['object']).columns:
                    le = LabelEncoder()
                    X[column] = le.fit_transform(X[column])
                    label_encoders[column] = le
                
                print("encoder done")
                
                # mi_classif = mutual_info_classif(X, y)
                # feature_relevance_dict = {col: float(score) for col, score in zip(X.columns, mi_classif)}

                # 检查数据类型并转换为浮点数
                X = X.apply(pd.to_numeric, errors='coerce')
                y = LabelEncoder().fit_transform(y)
                # 处理缺失值
                # 删除包含缺失值的行
                combined = pd.concat([X, pd.Series(y, name=label_column, index=X.index)], axis=1)
                combined = combined.dropna()

                X_encoded = combined.drop(columns=[label_column])
                y_encoded = combined[label_column]
                #mi_scores = {col: normalized_mutual_information(X.iloc[:, i], y) for i, col in enumerate(df.drop(columns=[label_column]).columns)}
                mi_scores = {col: normalized_mutual_info_score(X.iloc[:, i], y) for i, col in enumerate(df.drop(columns=[label_column]).columns)}
                return mi_scores, X_encoded, y_encoded

            def cal_feature_importance(df, label_column, model):
                if model:
                    print("model exists")
                    feature_importances = model.feature_importances_
                    # 计算25%和75%分位数
                    lower_quantile = np.percentile(feature_importances, 25)
                    upper_quantile = np.percentile(feature_importances, 75)
                    # 分配权重
                    weights = np.where(feature_importances <= lower_quantile, 1,
                                    np.where(feature_importances >= upper_quantile, 2, 0.5))
                    # 计算加权特征重要性
                    weighted_importances = feature_importances * weights
                    # 实际加权总和
                    actual_total = np.sum(weighted_importances)
                    # 计算可能的最小总和和最大总和
                    min_total = np.sum(feature_importances * np.min(weights))
                    max_total = np.sum(feature_importances * np.max(weights))
                    # 归一化总分
                    normalized_total_score = (actual_total - min_total) / (max_total - min_total)
                    metric_feature_importance = normalized_total_score

                else:
                    mi_scores, _, _ = cal_mutual_information(df, label_column)
                    low_relevancy_features = [col for col, mi in mi_scores.items() if mi <= 0.1]
                    low_relevancy_features_ratio = len(low_relevancy_features) / (num_columns-1)
                    metric_feature_importance = 1 - low_relevancy_features_ratio

                return metric_feature_importance
            
            metrics['feature_relevance'] = cal_feature_importance(df, label_column, model)

            

            '''--------target leakage----------'''
            #threshold = 0.95
            mi_scores, X_encoded, y_encoded = cal_mutual_information(df, label_column)
            target_leakage_features = [col for col, mi in mi_scores.items() if mi >= 0.95]
            num_target_leakage_features = len(target_leakage_features)
            target_leakage_ratio = num_target_leakage_features / (num_columns-1)
            metrics['target_leakage_ratio'] = 1 - target_leakage_ratio
            print("target leakage calculated")


            '''--------feature correlation----------'''
            # based on mutual infomation, threshold = 0.8
            X_df = pd.DataFrame(X_encoded, columns=df.drop(columns=[label_column]).columns)
            corr_column = X_df.columns
            n_features = len(corr_column)
            correlation_matrix = pd.DataFrame(np.zeros((len(corr_column), len(corr_column))), index=corr_column, columns=corr_column)
            highly_dependent_count = 0
            total_feature_pairs = (n_features * (n_features - 1)) / 2  # 计算特征对总数

            for i, col1 in enumerate(corr_column):
                for j, col2 in enumerate(corr_column):
                    if i < j:
                        nmi = normalized_mutual_info_score(X_encoded[col1], X_encoded[col2])
                        correlation_matrix.loc[col1, col2] = nmi
                        correlation_matrix.loc[col2, col1] = nmi
                        if nmi >= 0.8:
                            highly_dependent_count += 1

            highly_dependent_rate = highly_dependent_count / total_feature_pairs if total_feature_pairs > 0 else 0

            feature_correlation_dict = {
                f'{feature1}_and_{feature2}': float(correlation_matrix.loc[feature1, feature2])
                for feature1 in corr_column for feature2 in corr_column if feature1 != feature2
            }

            metrics['feature_correlation'] = 1 - highly_dependent_rate
            print("feature correlation calculated")

            '''----------------------Construct weights and pillars dict---------------------'''

            weights = {
                'extra_fields': extra_fields_weight,
                'missing_values_ratio': missing_values_ratio_weight,
                'inconsistent_column': inconsistent_column_weight,
                'duplicate_rows': duplicate_rows_weight,
                'duplicate_columns': duplicate_columns_weight,
                'constant_features': constant_features_weight,
                'outlier_ratio': outlier_ratio_weight,
                'label_purity': label_purity_weight,
                'class_imbalance_ratio': class_imbalance_ratio_weight,
                'feature_relevance': feature_relevance_weight,
                'target_leakage_ratio': target_leakage_ratio_weight,
                'feature_correlation': feature_correlation_weight,
                'pillar_feature_relevance': pillar_feature_relevance_weight,
                'pillar_uniqueness': pillar_uniqueness_weight,
                'pillar_consistency': pillar_consistency_weight
            }

            def construct_weights_dict(weights):
                weights_all = {
                    "consistency": {
                        "pillar_score" : weights['pillar_consistency'],
                        "extra_fields": weights['extra_fields'],
                        "inconsistent_column": weights['inconsistent_column'],
                    },
                    "uniqueness": {
                        "pillar_score" : weights['pillar_uniqueness'],
                        "duplicate_rows": weights['duplicate_rows'],
                        "duplicate_columns": weights['duplicate_columns'],
                    },
                    "feature_relevance": {
                        "pillar_score" : weights['pillar_feature_relevance'],
                        "constant_features": weights['constant_features'],
                        "feature_relevance": weights['feature_relevance'],
                    },
                    "completeness": {
                        "pillar_score" : weights['missing_values_ratio']
                    },
                    "outlier_detection": {
                        "pillar_score" : weights['outlier_ratio']
                    },
                    "label_purity": {
                        "pillar_score" : weights['label_purity']
                    },
                    "class_parity": {
                        "pillar_score" : weights['class_imbalance_ratio']
                    },
                    "target_leakage": {
                        "pillar_score" : weights['target_leakage_ratio']
                    },
                    "feature_correlation": {
                        "pillar_score" : weights['feature_correlation']
                    }
                }
                return weights_all
            
            def construct_pillars_dict(metrics):
                pillars = {
                    "consistency": {    
                        "extra_fields": metrics['extra_fields'],
                        "inconsistent_column": metrics['inconsistent_column'],
                    },
                    "uniqueness": {
                        "duplicate_rows": metrics['duplicate_rows'],
                        "duplicate_columns": metrics['duplicate_columns'],
                    },
                    "feature_relevance": {
                        "constant_features": metrics['constant_features'],
                        "feature_relevance": metrics['feature_relevance'],
                    },
                    "completeness": {
                        "pillar_score" : metrics['missing_values_ratio']
                    },
                    "outlier_detection": {
                        "pillar_score" : metrics['outlier_ratio']
                    },
                    "label_purity": {
                        "pillar_score" : metrics['label_purity']
                    },
                    "class_parity": {
                        "pillar_score" : metrics['class_imbalance_ratio']
                    },
                    "target_leakage": {
                        "pillar_score" : metrics['target_leakage_ratio']
                    },
                    "feature_correlation": {
                        "pillar_score" : metrics['feature_correlation']
                    }
                }
                return pillars
            
            def transform_scores(dict):
                transformed_dict = {}
                for pillar_name, metrics in dict.items():
                    transformed_metrics = {}
                    for metric_name, value in metrics.items():
                        # 将值从0-1转换为1-100并保留一位小数
                        transformed_value = round(value * 100, 1)
                        transformed_metrics[metric_name] = transformed_value
                    transformed_dict[pillar_name] = transformed_metrics
                return transformed_dict
            
            def weighted_average(metric_values, weights):
                total_weight = sum(weights)
                normalized_weights = [w / total_weight for w in weights]
                weighted_avg = sum(s * w for s, w in zip(metric_values, normalized_weights))
                return weighted_avg
            
            def pillar_aggregator(metrics, weights, metric_names):
                values = [metrics[name] for name in metric_names]
                pillar_wise_weights = [weights[name] for name in metric_names]
                return weighted_average(values, pillar_wise_weights)

            def overall_aggregator(metrics, weights):
                pillars = {}

                for pillar_name, metric_scores in metrics.items():
                    pillar_weights = weights[pillar_name]
                    metric_names = list(metric_scores.keys())
                    pillar_score = pillar_aggregator(metric_scores, pillar_weights, metric_names)
                    metric_scores['pillar_score'] = pillar_score
                    pillars[pillar_name] = metric_scores

                overall_pillar_scores = [pillar['pillar_score'] for pillar in pillars.values()]
                overall_pillar_weights = [weights['pillar_score'] for weights in weights.values()]
                overall_score = weighted_average(overall_pillar_scores, overall_pillar_weights)

                pillars = transform_scores(pillars)

                overall_score = round(overall_score * 100, 1)
                pillars['overall'] = overall_score
                
                return pillars

            metrics_construct = construct_pillars_dict(metrics)
            weights_construct = construct_weights_dict(weights)

            # calculate all the pillar scores and overall score, write them to the dicts
            pillars = overall_aggregator(metrics_construct, weights_construct)
            
            return pillars
        
        print(len(df))
        #label_column = "Label(LEGITIMATE:Botnet:Background)"
        pillars_response = cal_metrics(df, label_column)
        print(df.head())
        print(pillars_response)
        
    # Respond back to the frontend
    return jsonify(pillars_response), 200