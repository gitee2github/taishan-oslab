// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'
import ElementUI from 'element-ui'
import 'bootstrap/dist/css/bootstrap.min.css'
import ElTablePagination from 'el-table-pagination'

// 注册到全局
Vue.use(ElementUI)
Vue.use(ElTablePagination)

if (process.env.NODE_ENV === 'development') {
  axios.defaults.baseURL = 'http://122.9.36.214:81/'
  console.log(`Using baseURL ${axios.defaults.baseURL} in development mode.`)
  const token = localStorage.getItem('auth_token')
  if (token) {
    axios.defaults.headers = {
      'Authorization': token
    }
  } else {
    console.warn('`auth_token` is not set, Authorization header won\'t be used.')
  }
}

Vue.prototype.$http = axios
Vue.prototype.$stuTblHandler = function(o) {
  this.$router.push('/student/' + o.stu)
  window.scrollTo(0, 0)
}
Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
