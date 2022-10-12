<template>
  <div id="app">
    <div align="center">
      <el-button type="success" :loading="isLoading" @click.native="fetch_data">刷新</el-button>
    </div>
    <div id="scoreChart" style="width:100%; height:600px;"></div>
  </div>
</template>

<script>
var echarts = require('echarts')
export default {
  data: function() {
    return {
      isLoading: true,
      teachers: [],
      students: [],
      columns: [],
      labs: [],
      exams: [],
      time: [],
      score: [],
      chartColumn: null,
      option: {
        title: {
        },
        tooltip: { trigger: 'axis' },
        toolbox: {
          show: true,
          bottom: '0%',
          itemSize: 20,
          iconStyle: {
            borderColor: '#000'
          },
          feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            saveAsImage: { show: true }
          }
        },
        legend: {
          data: [],
          type: 'scroll',
          left: 'center',
          selected: {},
          inactiveColor: '#666',
          textStyle: {
            fontSize: 20
          }
        },
        xAxis: {
          name: '时间',
          type: 'time',
          splitNumber: 12,
          color: '#555',
          axisLabel: {
            show: true,
            textStyle: {
              color: '#000',
              fontSize: '14'
            }
          }
        },
        yAxis: {
          name: '100分人数',
          type: 'value',
          axisLabel: {
            show: true,
            textStyle: {
              color: '#000',
              fontSize: '15'
            }
          }
        },
        series: []
      },
      option_exam: {
        title: {},
        tooltip: { trigger: 'axis' },
        toolbox: {
          show: true,
          bottom: '0%',
          itemSize: 20,
          iconStyle: {
            borderColor: '#000'
          },
          feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            saveAsImage: { show: true }
          }
        },
        legend: {
          data: [],
          type: 'scroll',
          selected: {},
          inactiveColor: '#666',
          textStyle: {
            fontSize: 20
          }
        },
        xAxis: {
          name: '时间',
          type: 'time',
          splitNumber: 8,
          axisLabel: {
            show: true,
            textStyle: {
              color: '#000',
              fontSize: '14'
            }
          }
        },
        yAxis: {
          name: '100分人数',
          type: 'value',
          axisLabel: {
            show: true,
            textStyle: {
              color: '#000',
              fontSize: '15'
            }
          }
        },
        series: []
      }
    }
  },
  created() {
    this.fetch_data()
  },
  methods: {
    fetch_data: function() {
      this.param_init()
      this.isLoading = true
      var self = this
      this.$http.get('/json/scores').then(response => {
        this.teachers = response.data.teachers
        this.columns = response.data.columns
        this.students = response.data.students
        this.columns.forEach(function(item) {
          if (item.title.startsWith('lab') && !item.isExam) {
            self.labs.push(item.title)
          }
          if (item.isExam) {
            self.exams.push(item.title)
          }
        })
        this.get_time_and_sort()
        this.chartInit()
        this.draw(this.labs)
        this.drawExam(this.exams)
        this.isLoading = false
      })
    },
    param_init: function() {
      this.labs = []
      this.exams = []
      this.teachers = []
      this.columns = []
      this.students = []
      this.time = []
      this.score = []
    },
    get_time_and_sort: function() {
      var self = this
      var labs = this.labs.concat(this.exams)
      labs.forEach(function(lab) {
        var temp = []
        self.students.forEach(function(student) {
          if (student[lab] === 100) {
            temp.push(student[lab + '.time'])
          }
        })
        temp.sort(function(a, b) {
          return a > b ? 1 : -1
        })
        self.time.push({ lab: lab, time: temp })
      })
    },
    draw: function(labsName) {
      var self = this
      labsName.forEach(function(labName) {
        self.time.forEach(function(temp) {
          if (temp.lab === labName) {
            var datas = []
            temp.time.forEach(function(time, index) {
              datas.push({ name: time, value: [time, index + 1] })
            })
            self.option.legend.data.push(labName)
            self.option.legend.selected[labName] = false
            self.option.series.push({
              name: labName,
              type: 'scatter',
              smooth: true,
              data: datas,
              symbolSize: 6
            })
          }
        })
      })
      self.chartColumn.setOption(self.option)
    },
    drawExam: function(labsName) {
      var self = this
      labsName.forEach(function(labName) {
        self.time.forEach(function(temp) {
          if (temp.lab === labName) {
            var datas = []
            temp.time.forEach(function(time, index) {
              datas.push({ name: time, value: [time, index + 1] })
            })
          }
        })
      })
    },
    chartInit: function() {
      this.option.series = []
      this.chartColumn = echarts.init(document.getElementById('scoreChart'))
      this.chartColumn.setOption(this.option)
    }
  }
}
</script>
