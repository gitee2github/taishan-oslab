<template>
<el-container>
  <el-header>
    <el-menu
      class="el-menu-demo"
      default-active="1"
      mode="horizontal"
      background-color="#4e9fe6"
      text-color="#FFFFFF"
      active-text-color="#FFFFFF"
      style="text-align: center; width:100%;">
      <el-menu-item index="1" style="text-align: center;">
        <router-link to="/">课下实验</router-link>
      </el-menu-item>
      <el-menu-item index="2">
        <router-link to="/graph">分数统计</router-link>
      </el-menu-item>
      <el-menu-item index="3">
        <router-link to="/leaderboard">排行榜</router-link>
      </el-menu-item>
      <el-menu-item index="4">
        <router-link to="/lab">实验统计</router-link>
      </el-menu-item>
      <el-menu-item index="7">
        <router-link to="/student">学生统计</router-link>
      </el-menu-item>
    </el-menu>
  </el-header>
  <el-main>
    <router-view></router-view>
  </el-main>
</el-container>
</template>

<script type="text/ecmascript-6">
import ElContainer from 'element-ui/packages/container/src/main'
export default {
  components: { ElContainer }
}
</script>

<style>
  a:link {
    text-decoration: none;
  }
  .router-link-active {
    text-decoration: none;
  }
  .el-menu{
    justify-content: center;
  }

  .stu-table .el-table__row {
    cursor: pointer;
  }

  li.el-menu-item {
    padding: 0;
  }

  li a {
    display: inline-block;
    padding: 0 20px;
    font-size: 18px;
  }
</style>
