<template>
  <div class="wrapper">
    <side-bar>
      <template slot="links">
        <sidebar-link
          to="/home"
          name='Home'
          icon="tim-icons icon-bank"
        />
        <sidebar-link
          to="/config"
          name='Assessment Setup'
          icon="tim-icons icon-attach-87"
        />
        <sidebar-link
          to="/result"
          name='Assessment Result'
          icon="tim-icons icon-chart-bar-32"
        />
      </template>
    </side-bar>
    <div class="main-panel">
      <top-navbar></top-navbar>

      <dashboard-content @click.native="toggleSidebar"> </dashboard-content>

      <content-footer></content-footer>
    </div>
  </div>
</template>
<style lang="scss"></style>
<script>
import TopNavbar from "./SampleNavbar.vue";
import ContentFooter from "./SampleFooter.vue";
import DashboardContent from "./Content.vue";
export default {
  components: {
    TopNavbar,
    ContentFooter,
    DashboardContent,
  },
  methods: {
    toggleSidebar() {
      if (this.$sidebar.showSidebar) {
        this.$sidebar.displaySidebar(false);
      }
    },
  },
};
</script>