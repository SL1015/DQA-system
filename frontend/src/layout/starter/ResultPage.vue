<template>
  <div class="row">
    <div class="row">
      <!-- Show this message and link if no request has been made yet -->
      <div v-if="!isLoading && !result && !error">
        <p>Please submit an assessment request first. </p>
        <router-link to="/config">Start here</router-link>
      </div>
    </div>
    <div class="col-md-12" v-if="result">
      <div class="row d-flex" style="display: flex; align-items: stretch;">
        <div class="col-md-3 d-flex" style="display: flex;">
          <card class="flex-fill">
            <h3 slot="header" class="card-title">Overall DQ Score</h3>
            <circular-progress-bar :value="result.overall" :size="230" color="#e6735b"></circular-progress-bar>
          </card>
        </div>
          <!-- Blue Bar Chart -->
        <div class="col-md-9 d-flex" style="display: flex;">
          <card class="flex-fill" type="chart">
            <h3 slot="header" class="card-title">Pillar Scores</h3>
            <div class="chart-area  flex-fill">
              <bar-chart
                style="height: 100%"
                chart-id="result-bar-chart"
                :chart-data="barChartData"
                :gradient-stops="blueBarChart.gradientStops"
                :extra-options="blueBarChart.extraOptions"
              ></bar-chart>
            </div>
          </card>
        </div>

        <div class="col-md-6">
          <card class="flex-fill fixed-card-height">
            <h3 slot="header" class="card-title">Consistency</h3>
            <div class="progress-bars">
              <div class="large-bar">
                <h5 class="large-title">Overall</h5>
                <circular-progress-bar :value="result.consistency.pillar_score" :size="200"></circular-progress-bar>
              </div>
              <div class="small-bars">
                <h5 class="small-title">Inconsistent Column</h5>
                <circular-progress-bar :value="result.consistency.inconsistent_column" :size="140" color="#1d8cf8"></circular-progress-bar>
                <h5 class="small-title">Extra Fields</h5>
                <circular-progress-bar :value="result.consistency.extra_fields" :size="140" color="#1d8cf8"></circular-progress-bar>
              </div>
            </div>
          </card>
        </div>

        <div class="col-md-6">
          <card class="flex-fill fixed-card-height">
            <h3 slot="header" class="card-title">Uniqueness</h3>
            <div class="progress-bars">
              <div class="large-bar">
                <h5 class="large-title">Overall</h5>
                <circular-progress-bar :value="result.uniqueness.pillar_score" :size="200"></circular-progress-bar>
              </div>
              <div class="small-bars">
                <h5 class="small-title">Duplicate Columns</h5>
                <circular-progress-bar :value="result.uniqueness.duplicate_columns" :size="140" color="#1d8cf8"></circular-progress-bar>
                <h5 class="small-title">Duplicate Rows</h5>
                <circular-progress-bar :value="result.uniqueness.duplicate_rows" :size="140" color="#1d8cf8"></circular-progress-bar>
              </div>
            </div>
          </card>
        </div>

        <div class="col-md-6">
          <card class="flex-fill fixed-card-height">
            <h3 slot="header" class="card-title">Feature Relevance</h3>
            <div class="progress-bars">
              <div class="large-bar">
                <h5 class="large-title">Overall</h5>
                <circular-progress-bar :value="result.feature_relevance.pillar_score" :size="200"></circular-progress-bar>
              </div>
              <div class="small-bars">
                <h5 class="small-title">Constant Features</h5>
                <circular-progress-bar :value="result.feature_relevance.constant_features" :size="140" color="#1d8cf8"></circular-progress-bar>
                <h5 class="small-title">Feature Importance</h5>
                <circular-progress-bar :value="result.feature_relevance.feature_relevance" :size="140" color="#1d8cf8"></circular-progress-bar>
              </div>
            </div>
          </card>
        </div>

        <div class="col-md-3 d-flex" style="display: flex;">
          <card class="flex-fill">
            <h3 slot="header" class="card-title">Label Purity</h3>
            <div class="large-bar">
              <h5 class="small-title">Inconsistent Label</h5>
              <circular-progress-bar :value="result.label_purity.pillar_score"></circular-progress-bar>
            </div>
          </card>
        </div>
        <div class="col-md-3 d-flex" style="display: flex;">
          <card class="flex-fill">
            <h3 slot="header" class="card-title">Target Leakage</h3>
            <div class="large-bar">
              <h5 class="small-title">Extreme Feature Importance</h5>
              <circular-progress-bar :value="result.target_leakage.pillar_score"></circular-progress-bar>
            </div>
          </card>
        </div>

        <div class="col-md-3 d-flex" style="display: flex;">
          <card class="flex-fill fixed-card-height">
            <h3 slot="header" class="card-title">Completeness</h3>
            <div class="large-bar">
              <h5 class="small-title">Missing Values</h5>
              <circular-progress-bar :value="result.completeness.pillar_score"></circular-progress-bar>
            </div>
          </card>
        </div>

        <div class="col-md-3 d-flex" style="display: flex;">
          <card class="flex-fill">
            <h3 slot="header" class="card-title">Outlier Detection</h3>
            <div class="large-bar">
              <h5 class="small-title">Numeric Outliers</h5>
              <circular-progress-bar :value="result.outlier_detection.pillar_score"></circular-progress-bar>
            </div>
          </card>
        </div>

        <div class="col-md-3 d-flex" style="display: flex;">
          <card class="flex-fill">
            <h3 slot="header" class="card-title">Class Parity</h3>
            <div class="large-bar">
              <h5 class="small-title">Class Imbalance Ratio</h5>
              <circular-progress-bar :value="result.class_parity.pillar_score"></circular-progress-bar>
            </div>
          </card>
        </div>
        <div class="col-md-3 d-flex" style="display: flex;">
          <card class="flex-fill">
            <h3 slot="header" class="card-title">Feature Correlation</h3>
            <div class="large-bar">
              <circular-progress-bar :value="result.feature_correlation.pillar_score"></circular-progress-bar>
            </div>
          </card>
        </div>
        

      </div>
    </div>
    <p v-if="error" class="error"> Error: {{ error }}</p>
    
  </div>
</template>

<script>
import BarChart from "@/components/Charts/BarChart";
import * as chartConfigs from "@/components/Charts/config";
import config from "@/config";
import CircularProgressBar from '@/components/CircularProgressBar.vue';

export default {
  name: "ResultPage",
  components: {
    BarChart,
    CircularProgressBar
  },
  data() {
    return {
      result: null,
      error: null,
      isLoading: false, // Initially false to indicate no loading
      barChartData: {
        labels: [], // X-axis labels
        datasets: [
          {
            label: "Pillar Score",
            fill: true,
            borderColor: config.colors.info,
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            data: [], // Y-axis values
          },
        ],
      },
      blueBarChart: {
        extraOptions: chartConfigs.barChartOptions,
        gradientColors: config.colors.primaryGradient,
        gradientStops: [1, 0.4, 0], // Customize as needed
      },
    };
  },
  created() {
    this.updateStateFromRoute();
  },
  watch: {
    '$route': 'updateStateFromRoute', // React to route changes
    result: {
      immediate: true,
      handler(newValue) {
        if (newValue) {
          this.prepareChartData(newValue);
        }
      },
    },
  },
  methods: {
    updateStateFromRoute() {
      // 开始请求时更新result page的isLoading状态
      this.isLoading = this.$route.params.isLoading || false;
      
      this.error = !this.isLoading && this.$route.params.error || null;
      console.log('error:', this.error);
      console.log('error raw:', this.$route.params.error);
      // 如果请求完成，且存在result，parse result
      this.result = !this.isLoading && this.$route.params.result ? this.$route.params.result : null;
      if (this.result) {
        this.prepareChartData(this.result);
      }
    },
    formatKey(key) {
    return key
        .split('_')                   // 以下划线分割字符串
        .map(word => word.charAt(0).toUpperCase() + word.slice(1)) // 将每个单词的首字母转换为大写
        .join(' ');                   // 用空格连接单词
    },
    prepareChartData(result) {
      const names = [];
      const scores = [];

      for (const key in result) {
        if (result.hasOwnProperty(key) && result[key].pillar_score !== undefined) {
          names.push(this.formatKey(key)); // Use formatted key as the label
          scores.push(result[key].pillar_score); // Extract the pillar_score for the data
        }
      }

      this.barChartData.labels = names;
      this.barChartData.datasets[0].data = scores;

      console.log('Chart Data:', this.barChartData); // Log the chart data to ensure it's correct
    },
  },
};
</script>

<style scoped>
.row {
  margin-bottom: 15px;
  margin-left: 5px;
  margin-right: 5px;
}
.result-content {
  margin-top: 10px;
}
.error {
  color: red;
}
pre {
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
}
.chart-area {
  height: 400px; /* Adjust as needed */
}
.progress-bars {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.small-bars {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px; /* Adjust the gap as needed */
}
.fixed-card-height {
  height: 380px; /* Set a fixed height for the card */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.large-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.small-title, .large-title {
  margin-bottom: 5px; /* Reduce the bottom margin to decrease the space between label and progress bar */
}

</style>
