<template>
  <div class="container">
    <h2 slot="header" class="text-primary">Welcome to Data Quality Assessment System</h2>

    <h5>Data quality assessment (DQA) is critical in AI systems
      because the quality of data directly impacts the performance and accuracy of AI models. 
      This DQA system ensures that data is accurate, reliable, and suitable for its intended use. 
      The assessment is conducted using both traditional pillars and AI-related pillars. 
      Each pillar encompasses specific metrics that measure different aspects of data quality.  
      By systematically assessing these metrics, the system provides a comprehensive evaluation of the dataset's quality, ensuring that your AI system can make precise predictions.</h5>

    <router-link to="/config">Start here</router-link>
  </div>
</template>
<script>
export default {
  name: "home-page",
  data() {
    return {};
  },
};
</script>
<style>
.container {
  padding: 10px;
}
h2 {
  color: #00d6b4 !important;
}
</style>