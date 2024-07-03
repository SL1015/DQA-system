

import Vue from "vue";
import Router from "vue-router";
import DashboardLayout from "../layout/starter/SampleLayout.vue";
import HomePage from "../layout/starter/HomePage.vue";
import ResultPage from "../layout/starter/ResultPage.vue";
import ConfigPage from "../layout/starter/Configurations.vue";


Vue.use(Router);

export default new Router({
  routes: [
    {
      path: "/",
      name: "home",
      redirect: "/home",
      component: DashboardLayout,
      children: [
        {
          path: "home",
          name: "Home",
          components: { default: HomePage },
        },
        {
          path: "result",
          name: "Assessment Result",
          components: { default: ResultPage },
          props: true,
        },
        {
          path: "config",
          name: "Assessment setup",
          components: { default: ConfigPage },
        },
      ],
    },
  ],
});

