<template>
  <div>
  <div>
    <div style="text-align: center;" float="left">
      <el-radio-group v-model="radio">
        <el-radio-button label="全部" v-on:click.native="set_origin"></el-radio-button>
        <el-radio-button v-for="teacher in teachers" :key="teacher.id"
                         :label=teacher.zhname v-on:click.native="filter_students(teacher.codename)">
        </el-radio-button>
      </el-radio-group>

      <el-button type="success" :loading="isLoading" @click.native="fetch_data">刷新</el-button>
    </div>
    <div style="text-align: center;">
      <el-table
        :data="tableData"
        style="width: 100%"
        header-cell-style = "background-color: #a5d5a5; color: #505050"
        align="center">
        <el-table-column
          fixed
          prop="实验"
          label="实验"
          min-width="110">
        </el-table-column>
        <el-table-column
          v-for="section in sections" :key="section.id"
          :prop=section
          :label=section
          min-width="60">
        </el-table-column>
      </el-table>
    </div>
  </div>
    <br>
  <div>
    <el-table
      class='stu-table'
      @row-click='o => this.$stuTblHandler(o)'
      :data="selected_students"
      style="width: 100%"
      header-cell-style = "background-color: #a0c5df; color: #505050">
      <el-table-column
        fixed
        sortable
        label="学号"
        min-width="90"
        prop="stu">
      </el-table-column>
      <el-table-column
        fixed
        sortable
        :sort-method="sortByPingyin"
        label="姓名"
        min-width="90"
        prop="name">
      </el-table-column>
      <el-table-column v-for="lab in labs" :key="lab.id"
        :prop=lab
        :label=lab
        min-width="65"
        sortable>
      </el-table-column>
    </el-table>
  </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [],
      scoreData: [],
      students: [],
      teachers: [],
      columns: [],
      selected_students: [],
      selected_teacher: 'ALL',
      labs: [],
      sections: [],
      isLoading: true,
      radio: '全部'
    }
  },
  created() {
    this.fetch_data()
  },
  methods: {
    set_origin: function() {
      this.selected_teacher = 'ALL'
      this.selected_students = this.students
      this.calculate_tableData()
    },
    filter_students: function(teacher) {
      this.selected_students = this.students.filter(function(item) {
        return item['teacher'] === teacher
      })
      this.selected_teacher = teacher
      this.calculate_tableData()
    },
    fetch_data: function() {
      this.isLoading = true
      var self = this
      this.$http.get('/json/scores').then(response => {
        this.teachers = response.data.teachers
        this.columns = response.data.columns
        this.students = response.data.students
        self.labs = []
        this.columns.forEach(function(item) {
          if (item.title.startsWith('lab') && item.isExam === false) {
            self.labs.push(item.title)
          }
        })
        if (this.selected_teacher === 'ALL') {
          this.selected_students = this.students
        } else {
          this.selected_students = this.students.filter(function(item) {
            return item['teacher'] === self.selected_teacher
          })
        }
        this.calculate_tableData()
        this.isLoading = false
      })
    },
    calculate_tableData: function() {
      var self = this
      self.tableData = []
      self.sections = ['100分', '90分以上', '80分以上', '70分以上', '60分以上',
        '50分以上', '10分以上', '0分']
      this.columns.forEach(function(name) {
        if (name.title.startsWith('lab') && name.isExam === false) {
          var tmp = {
            'title': name.title,
            'G010': 0,
            'G050': 0,
            'G060': 0,
            'G070': 0,
            'G080': 0,
            'G090': 0,
            'G100': 0,
            'E0': 0
          }
          self.selected_students.forEach(function(item) {
            const v = item[tmp.title]
            if (v <= 0) {
              tmp.E0 += 1
              return
            }
            if (v >= 10) {
              tmp.G010 += 1
            }
            if (v >= 50) {
              tmp.G050 += 1
            }
            if (v >= 60) {
              tmp.G060 += 1
            }
            if (v >= 70) {
              tmp.G070 += 1
            }
            if (v >= 80) {
              tmp.G080 += 1
            }
            if (v >= 90) {
              tmp.G090 += 1
            }
            if (v >= 100) {
              tmp.G100 += 1
            }
          })
          self.tableData.push({
            实验: tmp.title,
            '100分': tmp.G100,
            '90分以上': tmp.G090,
            '80分以上': tmp.G080,
            '70分以上': tmp.G070,
            '60分以上': tmp.G060,
            '50分以上': tmp.G050,
            '10分以上': tmp.G010,
            '0分': tmp.E0
          })
        }
      })
    },
    sortByPingyin: function(a, b) {
      return a.name.localeCompare(b.name)
    }
  }
}
</script>
