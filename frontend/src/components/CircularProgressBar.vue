<template>
  <div>
    <apexchart :type="type" :options="chartOptions" :series="[value]" :height="size" :width="size"></apexchart>
  </div>
</template>

<script>
import VueApexCharts from 'vue-apexcharts';

export default {
  components: {
    apexchart: VueApexCharts
  },
  props: {
    value: {
      type: Number,
      required: true
    },
    size: {
      type: Number,
      default: 200
    },
    color: {
      type: String,
      default: '#00d6b4' 
    },
    type: {
      type: String,
      default: 'radialBar'
    }
  },
  data() {
    return {
      chartOptions: {
        plotOptions: {
          radialBar: {
            hollow: {
              size: '65%', 
            },
            dataLabels: {
              name: {
                show: false,
              },
              value: {
                formatter: function (val) {
                  return `${val}`;
                },
                fontSize: '22px',
                color: '#FFFFFF',
                offsetY: 5,
              }
            }
          }
        },
        colors: [this.color],
        stroke: {
          lineCap: 'round'
        },
      }
    };
  }
};
</script>

<style scoped>
/* 可以根据需要添加自定义样式 */
</style>
