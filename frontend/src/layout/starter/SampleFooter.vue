<template>
  <footer class="footer">
    <div class="container-fluid">
      <div class="copyright">
        © {{ year }} Developed by Shushi Luo. <i class="tim-icons icon-heart-2"></i>
      </div>
    </div>
  </footer>
</template>
<script>
export default {
  data() {
    return {
      year: new Date().getFullYear(),
    };
  },
};
</script>
<style></style>
