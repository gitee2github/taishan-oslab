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
      <el-button type="success" :loading="isLoading" @click.native="fetch_data">刷新成绩</el-button>
    </div>
    <div style="text-align: center;" float="left">
      <el-radio-group v-model="radio2">
        <el-radio-button label="全部" v-on:click.native="generate_by_lab('all')"></el-radio-button>
        <el-radio-button v-for="lab in labs" :key="lab.id"
                         :label=lab v-on:click.native="generate_by_lab(lab)">
        </el-radio-button>
      </el-radio-group>
    </div>
  </div>
  <div>
    <el-table
      class='stu-table'
      @row-click='o => this.$stuTblHandler(o)'
      :data="tableData"
      :default-sort = "{prop: 'score', order: 'descending'}"
      style="width: 100%"
      header-cell-style = "background-color: #a0c5df; color: #505050">
      <el-table-column
        label="排名"
        type="index">
      </el-table-column>
      <el-table-column
        label="学号"
        prop="stu">
      </el-table-column>
      <el-table-column
        label="姓名"
        prop="name">
      </el-table-column>
      <el-table-column
        prop="score"
        label="成绩"
        sortable
        :sort-orders="['descending', 'ascending']"
        :sort-method="sort_by_score_duration">
      </el-table-column>
      <el-table-column
        prop="duration"
        label="用时">
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
      labs: [],
      labReleaseDates: {},
      studentsSelected: [],
      teacherSelected: 'all',
      labSelected: 'all',
      tableData: [],
      isLoading: true,
      radio1: '全部',
      radio2: '全部',
      descending: true
    }
  },
  created() {
    this.fetch_data()
  },
  methods: {
    fetch_data: function() {
      this.isLoading = true
      this.$http.get('/json/scores').then(response => {
        this.students = response.data.students
        this.teachers = response.data.teachers
        this.columns = response.data.columns
        var labs = []
        var dates = {}
        this.columns.forEach(function(item) {
          if (item.title.startsWith('lab') && item.isExam === false) {
            labs.push(item.title)
            dates[item.title] = item['releaseDate']
          }
        })
        this.labs = labs
        this.labReleaseDates = dates
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
      this.generate_by_lab(this.labSelected)
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
    }
  }
}
</script>>
