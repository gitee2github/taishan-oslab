import Vue from 'vue'
import Router from 'vue-router'
import scoreNew from '../components/scoreNew.vue'
import graph from '../components/graph.vue'
import leaderboad from '../components/leaderboard.vue'
import qualification from '../components/qualification.vue'
import exam from '../components/exam.vue'
import lab from '../components/lab.vue'
import student from '../components/student.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'new',
      component: scoreNew
    },
    {
      path: '/graph',
      name: 'graph',
      component: graph
    },
    {
      path: '/leaderboard',
      name: 'leaderboard',
      component: leaderboad
    },
    {
      path: '/qualification',
      name: 'qualification',
      component: qualification
    },
    {
      path: '/exam',
      name: 'exam',
      component: exam
    },
    {
      path: '/lab/:id?',
      name: 'lab',
      component: lab
    },
    {
      path: '/student/:id?',
      name: 'student',
      component: student
    }
  ]
})
