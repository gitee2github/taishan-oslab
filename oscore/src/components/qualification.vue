<template>
  <div>
  <div>
    <div style="text-align: center;" float="left">
      <el-radio-group v-model="radio1">
        <el-radio-button label="全部" v-on:click.native="select_by_teacher('all')"></el-radio-button>
        <el-radio-button v-for="teacher in teachers" :key="teacher.id"
                         :label=teacher.zhname v-on:click.native="select_by_teacher(teacher.codename)">
        </el-radio-button>
      </el-radio-group>
      <el-button type="success" :loading="isLoading" @click.native="fetch_data">刷新</el-button>
    </div>
  </div>
  <el-dialog
    title=""
    width="60%"
    top="0"
    :visible.sync="dialogVisible"
    @close="onDialogClose">
    <div slot="title" class="header-title">
      <span>{{ currentDialogTitle }} - 提交记录</span>
    </div>
    <el-table
      :data="currentDialogData"
      v-loading = "isLoading"
      element-loading-background = "rgba(0, 0, 0, 0.5)"
      element-loading-text = "数据正在加载中"
      element-loading-spinner = "el-icon-loading">
      <el-table-column
        label="实验"
        prop="lab">
      </el-table-column>
      <el-table-column
        label="时间"
        prop="time">
      </el-table-column>
      <el-table-column
        label="截止时间"
        prop="deadline">
      </el-table-column>
      <el-table-column
        label="成绩"
        prop="score">
      </el-table-column>
    </el-table>
  </el-dialog>
  <div>
    <el-table
      class='stu-table'
      @row-click='o => this.$stuTblHandler(o)'
      :data="studentsSelected"
      style="width: 100%"
      header-cell-style = "background-color: #a0c5df; color: #505050; font-size: 4px">
      <el-table-column
        label="学号"
        prop="stu"
        width="90">
      </el-table-column>
      <el-table-column
        label="姓名"
        width="80"
        prop="name">
        <template slot-scope="scope">
          <a class='name' href="#" @click="onDialogOpen(scope.row.name, scope.row.stu)">{{ scope.row.name }}</a>
        </template>
      </el-table-column>
      <el-table-column
        label="申优资格"
        prop="name"
        :formatter="qualify"
        :filters="[{text: '有', value:'有'}, {text: '无', value:'无'}]"
        :filter-method="qualifyFilterHandler">
      </el-table-column>
      <el-table-column v-for="lab in labs" :key="lab.id" width="100"
        :label=lab>
        <template slot-scope="scope">
          <div slot="reference" class="name-wrapper">
            <span v-if="Date.parse(scope.row[lab + '.passtime']) < Date.parse(scope.row[lab + '.deadline'])" style="color:black"> {{scope.row[lab]}}</span>
            <span v-else style="color:red"> {{scope.row[lab]}}</span>
          </div>
        <!-- <el-popover trigger="hover" placement="top">
          <p>首次通过时间: {{ (scope.row[lab + '.passtime']) }}</p>
          <p>成绩: {{ scope.row[lab + '.passscore'] }}</p>
          <p>实验截止时间: {{ scope.row[lab + '.deadline'] }}</p>
          <div slot="reference" class="name-wrapper">
            <span v-if="Date.parse(scope.row[lab + '.passtime']) < Date.parse(scope.row[lab + '.deadline'])" style="color:black"> {{scope.row[lab]}}</span>
            <span v-else style="color:red"> {{scope.row[lab]}}</span>
          </div>
        </el-popover> -->
        </template>
      </el-table-column>
    </el-table>
  </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      students: [],
      teachers: [],
      columns: [],
      deadlines: {},
      labs: [],
      extras: [],
      studentsSelected: [],
      teacherSelected: 'all',
      isLoading: true,
      radio1: '全部',
      dialogVisible: false,
      currentDialogTitle: '',
      currentDialogData: []
    }
  },
  created() {
    this.fetch_data()
  },
  methods: {
    // count_extra: function(row, col, xx, index) {
    //   var count = 0
    //   this.extras.forEach(function(lab) {
    //     if (row[lab] >= 60) {
    //       count++
    //     }
    //   })
    //   return count
    // },
    qualify: function(row, col, xx, index) {
      var pass = 0
      for (const lab of this.labs) {
        if (lab.endsWith('-exam') || lab.endsWith('-Extra')) {
          if (row[lab + '.passtime'] === '' || Date.parse(row[lab + '.passtime']) > Date.parse(row[lab + '.deadline'])) {
            // exam or extra not pass
          } else {
            pass++
          }
        } else {
          if (row[lab + '.passtime'] === '' || Date.parse(row[lab + '.passtime']) > Date.parse(row[lab + '.deadline'])) {
            return '无'
          }
        }
      }
      if (pass >= 13) {
        return '有'
      }
      return '无'
      // // check labs
      // for (const lab of this.labs) {
      //   if (row[lab + '.passtime'] === '' || Date.parse(row[lab + '.passtime']) > Date.parse(row[lab + '.deadline'])) {
      //     return '无'
      //   }
      // }
      // // check extras
      // if (this.count_extra(row, col, xx, index) < 2) {
      //   return '无'
      // }
      // return '有'
    },
    fetch_data: function() {
      this.isLoading = true
      this.$http.get('/json/scores').then(response => {
        this.students = response.data.students
        this.teachers = response.data.teachers
        this.columns = response.data.columns
        var labs = []
        var extras = []
        // var deadlines = {}
        this.columns.forEach((item) => {
          if (!item.title.startsWith('lab')) {
            return
          }
          if (item.isExam === false) {
            labs.push(item.title)
          } else {
            extras.push(item.title)
          }
          this.deadlines[item.title] = item.deadline
        })
        // this.deadlines = deadlines
        this.labs = labs.concat(extras)
        this.extras = []
        this.select_by_teacher(this.teacherSelected)
        this.isLoading = false
      })
    },
    select_by_teacher: function(teacher) {
      this.teacherSelected = teacher
      if (teacher === 'all') {
        this.studentsSelected = this.students
      } else {
        this.studentsSelected = this.students.filter(function(item) {
          return item['teacher'] === teacher
        })
      }
    },
    generate_by_lab: function(lab) {
      var self = this
      this.labSelected = lab
      this.tableData = this.studentsSelected.map(function(item) {
        var score = 0
        var duration = 0
        if (lab === 'all') {
          self.labs.forEach(function(lab) {
            score += item[lab]
            var dur = Date.parse(item[lab + '.time']) - Date.parse(self.labReleaseDates[lab])
            duration += dur > 0 ? dur : 0
          })
        } else {
          score += item[lab]
          var dur = Date.parse(item[lab + '.time']) - Date.parse(self.labReleaseDates[lab])
          duration += dur > 0 ? dur : 0
        }
        return {'stu': item['stu'], 'name': item['name'], 'score': score, 'duration': (duration / 3600000).toFixed(1)}
      })
    },
    sort_by_score_duration: function(a, b) {
      return a.score !== b.score ? (a.score < b.score ? -1 : 1) : (Number(a.duration) >= Number(b.duration) ? -1 : 1)
    },
    onDialogOpen: function(name, uid) {
      this.dialogVisible = true
      this.currentDialogTitle = name
      this.isLoading = true
      this.$http.get('/json/scorelog/' + uid).then(response => {
        this.currentDialogData = response.data
        this.currentDialogData.forEach((item) => {
          item['deadline'] = this.deadlines[item.lab]
        })
        this.isLoading = false
      })
    },
    onDialogClose: function(done) {
      this.currentDialogData = []
      done()
    },
    qualifyFilterHandler: function(value, row, column) {
      const result = this.qualify(row)
      return result === value
    }
  }
}
</script>
<style scoped>
.name {
  color: #303133;
}
.name:hover {
  text-decoration: underline;
}
</style>
