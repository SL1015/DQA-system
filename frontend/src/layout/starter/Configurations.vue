<template>
  <div class="row">
    <card>
      <form @submit.prevent="uploadFile">
        <div class="row">
          <div class="col-md-12">
            <h2 class="card-title">Upload Dataset</h2>
            <input type="file" id="fileInput" name="file" @change="handleFileUpload" ref="fileInput" required>
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <h2 class="card-title">Upload Trained Model (Optinal)</h2>
            <input type="file" id="modelInput" name="model" @change="handleFileUpload" ref="modelInput">
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <h2 class="card-title">Label Column</h2>
            <base-input
              placeholder="Please enter the name of Label Column"
              v-model="labelColumn"
              required
            />
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <h2 class="card-title">Pillar Weights Setup</h2>
            <label>Setup weights for each DQA pillar and for the corresponding metrics.</label>
          </div>
        </div>
        <div class="row">
          <div class="col-md-4 pr-md-1">
            <h4 class="text-primary" data-toggle="tooltip" 
            title="Consistency refers to the extent to which data is presented in the same format
and compatible with previous data">Consistency</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.consistency_weight"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Consistency pillar. The weight should be between 0 and 1."
            />
            <base-input
              label="Extra Field Rate"
              type="number"
              v-model="formData.extra_fields"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the weight for Extra Field Rate. The weight should be between 0 and 1. 
This metric quantifies the level of structural consistency.
The existence of extra fields indicates that some samples do not conform to the correct schema of the dataset. "
            />
            <base-input
              label="Inconsistent Column Rate"
              type="number"
              v-model="formData.inconsistent_column"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the weight for Inconsistent Column Rate. The weight should be between 0 and 1.
The existence of inconsistent columns indicates that some samples do not conform to the correct format."
            />
          </div>

          <div class="col-md-4 pl-md-1">
            <h4 class="text-primary" data-toggle="tooltip"
            title="Uniqueness refers to the extent to which records in a dataset are distinct and not duplicated.">Uniqueness</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.uniqueness_weight"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Uniqueness pillar. The weight should be between 0 and 1."
            />
            <base-input
              label="Duplicate Row Rate"
              type="number"
              v-model="formData.duplicate_rows"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the weight for Duplicate Row Rate. The weight should be between 0 and 1.
The existence of duplicate rows indicates that some samples are repeated in the dataset."
            />
            <base-input
              label="Duplicate Column Rate"
              type="number"
              v-model="formData.duplicate_columns"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the weight for Duplicate Column Rate. The weight should be between 0 and 1.
Duplicate columns increase the dimensionality of the feature space without adding new information, 
which is more prone to overfitting, and results in higher computational costs."
            />
          </div>
          <div class="col-md-4 px-md-1">
            <h4 class="text-primary" data-toggle="tooltip"
              title="Completeness is defined as the extent to which data are not missing 
and have sufficient breadth, depth and scope for the task at hand.">Completeness</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.missing_values_ratio"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Completeness pillar. The weight should be between 0 and 1."
            />
          </div>
        </div>
        <div class="row">
          <div class="col-md-4 pr-md-1">
            <h4 class="text-primary" data-toggle="tooltip"
              title="Outliers are data points that are significantly different from other data points. 
Outlier detection helps to detect noise or errors in the dataset.">Outlier Detection</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.outlier_ratio"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Outlier Detection pillar. The weight should be between 0 and 1."
            />
          </div>
          <div class="col-md-4 px-md-1">
            <h4 class="text-primary" data-toggle="tooltip"
              title="Class parity measures how evenly the classes are distributed in a dataset. 
Class imbalance might lead to a bias in machine learning models, favoring the majority class."
>Class Parity</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.class_imbalance_ratio"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Class Parity pillar. The weight should be between 0 and 1."
            />
          </div>
          <div class="col-md-4 pl-md-1">
            <h4 class="text-primary" data-toggle="tooltip" title="Label purity measures the level of label consistency. 
Inconsistent labels, which occur when similar instances have different labels, introduce noise and confusion into the training data, leading to lower accuracy and poor generalization to new data.">Label Purity</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.label_purity"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Label Purity pillar. The weight should be between 0 and 1."
            />
          </div>
        </div>
        <div class="row">
          <div class="col-md-4 pr-md-1">
            <h4 class="text-primary" data-toggle="tooltip" title=" Feature relevance analyzes the relative importance of each feature with respect to the target variable or class.">Feature Relevance</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.feature_relevance_weight"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Feature Relevance pillar. The weight should be between 0 and 1."
            />
            <base-input
              label="Constant Feature Rate"
              type="number"
              v-model="formData.constant_features"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the weight for Constant Feature Rate. The weight should be between 0 and 1.
Constant feature ratio refers to the proportion of features in a dataset that have the same value across all samples.
Constant features provide no discriminative value for the model."
            />
            <base-input
              label="Feature Importance"
              type="number"
              v-model="formData.feature_relevance"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the weight for Feature Importance. The weight should be between 0 and 1.
Feature importance measures the relevance of each feature to the target variable or class."
            />
          </div>
          <div class="col-md-4 px-md-1">
            <h4 class="text-primary" data-toggle="tooltop" title="Feature correlation refers to the statistical relationship between two or more features in a dataset. It measures how changes in one feature are associated with changes in another feature.
High correlation between features can indicate redundancy, while low correlation can suggest independence.">Feature Correlation</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.feature_correlation"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Feature Correlation pillar. The weight should be between 0 and 1."
            />
          </div>
          <div class="col-md-4 pl-md-1">
            <h4 class="text-primary" data-toggle="tooltip" title="Target leakage occurs when a model includes features that contain information unavailable
at the time of prediction, leading to biased predictions.">Target Leakage</h4>
            <base-input
              label="Overall Weight"
              type="number"
              v-model="formData.target_leakage_ratio"
              step="0.1"
              required
              @input.native="validateFormData"
              data-toggle="tooltip"
              title="Please setup the overall weight for Target Leakage pillar. The weight should be between 0 and 1."
            />
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <button type="submit" class="btn btn-primary">Upload and Calculate</button>
            <h4 v-if="isProcessing" class="assessment-result-waiting">Waiting for assessment result... Please don't leave the page.</h4>
          </div>
        </div>
      </form>
    </card>
  </div>
</template>

<script>


export default {
  name: "ConfigPage",
  components: {

  },
  mounted() {
    $('[data-toggle="tooltip"]').tooltip(); 
  },
  data() {
    return {
      labelColumn: '',
      isProcessing: false,
      formData: {
        consistency_weight: 0.8,//
        extra_fields: 0.5,   //
        inconsistent_column: 0.6, //
        missing_values_ratio: 0.8, //
        uniqueness_weight: 0.7,
        duplicate_rows: 0, 
        duplicate_columns: 1,
        outlier_ratio: 0.8,
        class_imbalance_ratio: 0.9,
        label_purity: 0.7,
        feature_relevance_weight: 1,
        constant_features: 0.4,
        feature_relevance: 1,
        feature_correlation: 0.8,
        target_leakage_ratio: 1,
      },
      file: null,
      modelFile: null,
    };
  },
  methods: {
    validateFormData() {
      Object.keys(this.formData).forEach(key => {
        if (this.formData[key] < 0) this.formData[key] = 0;
        if (this.formData[key] > 1) this.formData[key] = 1;
      });
    },
    isParamsEqual(currentParams, newParams) {
    return Object.keys(newParams).every(key => currentParams[key] === newParams[key]);
    },
    handleFileUpload(event) {
      if (event.target.name === 'file') {
      this.file = event.target.files[0];
      } else if (event.target.name === 'model') {
        this.modelFile = event.target.files[0];
      }
    },
    async uploadFile() {
      const file = this.$refs.fileInput.files[0];
      const modelFile = this.$refs.modelInput.files ? this.$refs.modelInput.files[0] : null;
      if (!this.file) return; // Ensure there's a file selected
      const formData = new FormData();
      formData.append('file', file);
      if (modelFile){
        formData.append('modelFile', modelFile);}
      formData.append('labelColumn', this.labelColumn);
      for (const key in this.formData) {
        formData.append(key, this.formData[key]);
      }
      try {
        const targetRouteName = 'Assessment Result';
        const isLoadingRouteParam = { isLoading: true };
        this.isProcessing = true;
        // Check if the current route is the same and the params are not different
        // if (this.$router.currentRoute.name !== targetRouteName) {
        //   this.$router.push({ name: targetRouteName, params: isLoadingRouteParam });
        // }
        const response = await fetch('http://localhost:5000/assessment', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        if (data.error) {
          this.isProcessing = false;
          this.$router.push({ name: targetRouteName, params: { error: data.error, isLoading: false } })
          .then(() => {
            window.scrollTo(0, 0); // 滚动到页面顶部
          });
        } else {
          this.isProcessing = false;
          this.$router.push({ name: targetRouteName, params: { result: data, isLoading: false } })
          .then(() => {
            window.scrollTo(0, 0); // 滚动到页面顶部
          });
        }
      } catch (error) {
        this.isProcessing = false;
        this.$router.push({ name: targetRouteName, params: { error: error.message, isLoading: false } })
          .then(() => {
            window.scrollTo(0, 0); // 滚动到页面顶部
          });
      }
    },
  }
};
</script>

<style scoped>

.row {
  margin-bottom: 15px;
  margin-left: 5px;
  margin-right: 5px;
}

h2, h4 {
  margin: 10px 0;
}
h3 {
  margin: 5px 0;
}

h4 {
  color: #42b883;
}

h2 {
  color: "#42b883" ; /* Replace 'green' with your desired color */
}
.assessment-result-waiting {
  color: "#42b883"; /* Replace 'green' with your desired color */
}

</style>