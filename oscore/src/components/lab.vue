<template>
  <el-container>
    <el-main style='text-align: center'>
      <el-select :value='selectedLab' placeholder="选择实验" @change='changeLab'>
        <el-option
          v-for="lab in labs"
          :key="lab"
          :label="lab"
          :value="lab">
        </el-option>
      </el-select>
      <template v-if='selectedLab && info'>
        <el-divider></el-divider>
        <el-descriptions>
          <el-descriptions-item label="起始时间">{{formatTime(info.begin)}}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{formatTime(info.end)}}</el-descriptions-item>
        </el-descriptions>
        <el-table :data="classStatData">
          <el-table-column key='title' label='' prop='title'>
          </el-table-column>
          <el-table-column key='total' label='总计' prop='total'>
          </el-table-column>
          <el-table-column
            v-for="t in info.teachers"
            :key='t.codename'
            :label='t.zhname'
            :prop='t.codename'
          >
          </el-table-column>
        </el-table>
        <el-divider></el-divider>
        <el-radio-group v-model='selectedTeacher' @change='changeTeacher'>
          <el-radio-button
            label='全部'
          ></el-radio-button>
          <el-radio-button
            v-for='t in info.teachers'
            :key='t.codename'
            :label='t.zhname'
          ></el-radio-button>
        </el-radio-group>
      </template>
      <div id='chart_0' class='lab-chart'></div>
      <div id='chart_1' class='lab-chart'></div>
      <div id='chart_2' class='lab-chart'></div>
      <div id='chart_3' class='lab-chart'></div>
    </el-main>
  </el-container>
</template>

<script>
import formatDuration from 'format-duration'
import * as echarts from 'echarts'
import ecStat from 'echarts-stat'
import {formatTime} from '../util'

export default {
  data() {
    return {
      labs: [],
      info: null,
      selectedTeacher: '全部',
      chart_0: null,
      chart_1: null,
      chart_2: null,
      chart_3: null
    }
  },
  created() {
    this.fetch_data()
    this.$watch(
      () => this.$route.params,
      this.fetch_data
    )
  },
  mounted() {
    function makeChart(id) {
      const chart = echarts.init(document.getElementById(id))
      window.addEventListener('resize', () => chart.resize())
      return chart
    }
    this.chart_0 = makeChart('chart_0')
    this.chart_1 = makeChart('chart_1')
    this.chart_2 = makeChart('chart_2')
    this.chart_3 = makeChart('chart_3')
  },
  methods: {
    async fetch_data() {
      const {id} = this.$route.params
      let url = '/json/lab'
      if (id) {
        url += `?id=${id}`
      }
      const resp = (await this.$http.get(url)).data
      this.labs = resp.labs
      this.info = resp.info || null
      this.drawAll()
    },
    changeLab(id) {
      if (this.selectedLab !== id) {
        this.$router.push(`/lab/${id}`)
      }
    },
    drawAll() {
      const stat = this.selectedStat
      if (!stat) {
        for (const c of [this.chart_0, this.chart_1, this.chart_2, this.chart_3]) {
          c.clear()
        }
        return
      }
      function scoreTransform(data) {
        const res = []
        for (let i = 0; i < 100; i += 10) {
          res.push([i + 5, 0, i, i + 10, `${i} - ${i + 10}`])
        }
        for (const x of data) {
          const i = Math.min(9, Math.floor(x / 10))
          ++res[i][1]
        }
        return res
      }
      function makeTranform(desc) {
        return data => {
          const r = ecStat.histogram(data).data
          const n = stat.stu_num - data.length
          if (n) {
            let c = 0
            let d = 100
            if (r.length) {
              c = r[r.length - 1][3]
              if (r.length > 1) {
                d = r[r.length - 1][0] - r[r.length - 2][0]
              }
            }
            r.push({
              value: [c + d / 2, n, c, c + d, `${c} - ${c + d}`],
              label: {
                formatter: `${n}\n(未${desc})`
              },
              itemStyle: {
                color: 'rgba(245,34,34,0.5)'
              }
            })
          }
          return r
        }
      }
      this.draw(this.chart_0, stat.final_scores, '最终成绩分布', scoreTransform)
      this.draw(this.chart_1, stat.any_durs, '首次提交用时分布', makeTranform('提交'))
      this.draw(this.chart_2, stat.passed_durs, '首次通过用时分布', makeTranform('通过'))
      this.draw(this.chart_3, stat.full_durs, '首次满分用时分布', makeTranform('满分'))
    },
    draw(chart, data, title, transform) {
      if (chart !== this.chart_0 && data.length === 0) {
        chart.clear()
        chart.getDom().style = 'display: none;'
        return
      }
      chart.getDom().style = undefined
      const bins = transform(data)
      const size15 = {
        fontSize: 16
      }
      const option = {
        title: {
          text: title,
          left: 'center',
          top: 20
        },
        grid: {
          left: '3%',
          right: '3%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          boundaryGap: '5%',
          splitNumber: 10,
          nameTextStyle: size15,
          axisLabel: size15
        },
        yAxis: {
          name: '人数',
          nameTextStyle: size15,
          axisLabel: size15
        },
        series: [{
          name: 'height',
          type: 'bar',
          barWidth: '99%',
          label: {
            normal: {
              show: true,
              position: 'top',
              fontSize: 16
            }
          },
          data: bins
        }]
      }
      if (chart !== this.chart_0) {
        option.xAxis.axisLabel = {...size15, formatter: this.formatDur}
        option.xAxis.name = '用时'
      } else {
        option.xAxis.name = '成绩'
      }
      chart.setOption(option)
    },
    changeTeacher() {
      this.drawAll()
    },
    median(arr) {
      const mid = Math.floor(arr.length / 2)
      const nums = [...arr].sort((a, b) => a - b)
      return arr.length % 2 !== 0 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2
    },
    formatTime,
    formatDur(secs) {
      if (isNaN(secs) || !isFinite(secs)) {
        return '-'
      }
      return formatDuration(secs * 1000)
    }
  },
  computed: {
    teachersWithTotal() {
      if (!this.info) {
        return []
      }
      const stat = {}
      for (const t of this.info.teachers) {
        for (const [k, v] of Object.entries(t.stat)) {
          if (typeof v === 'number') {
            stat[k] = (stat[k] || 0) + v
          } else if (Array.isArray(v)) {
            if (!stat[k]) {
              stat[k] = []
            }
            stat[k].push(...v)
          }
        }
      }
      return [{
        codename: 'total', zhname: '全部', stat
      }, ...this.info.teachers]
    },
    classStatData() {
      const rows = []
      const addRow = (key, title) => {
        const o = {title}
        if (typeof key === 'string') {
          for (const t of this.teachersWithTotal) {
            o[t.codename] = t.stat[key]
          }
        } else {
          for (const t of this.teachersWithTotal) {
            o[t.codename] = key(t.stat)
          }
        }
        rows.push(o)
      }
      addRow('stu_num', '选课人数')
      addRow('stu_num_full', '满分人数')
      addRow('stu_num_passed', '通过人数')
      addRow('stu_num_zero', '0 分人数')
      addRow('sub_num', '总提交次数')

      const addAvgRow = (key, desc) => {
        addRow(s => s.stu_num === 0 ? '-' : (s[key] / s.stu_num).toFixed(3), '平均' + desc + '提交次数')
      }
      addAvgRow('sub_num', '')
      addAvgRow('sub_num_before_passed', '通过所需')
      addAvgRow('sub_num_before_full', '满分所需')

      const addDurRows = (key, desc) => {
        addRow(s => this.formatDur(Math.min(...s[key])), '最早首次' + desc + '提交用时')
        addRow(s => this.formatDur(Math.max(...s[key])), '最晚首次' + desc + '提交用时')
        addRow(s => this.formatDur(this.median(s[key])), '中位首次' + desc + '提交用时（已提交学生）')
        addRow(s => {
          const arr = [...s[key]]
          while (arr.length < s.stu_num) {
            arr.push(Infinity)
          }
          return this.formatDur(this.median(arr))
        }, '中位首次' + desc + '提交用时（全体学生）')
      }
      addDurRows('any_durs', '')
      addDurRows('passed_durs', '通过')
      addDurRows('full_durs', '满分')

      return rows
    },
    selectedLab() {
      return this.$route.params.id
    },
    selectedStat() {
      for (const t of this.teachersWithTotal) {
        if (t.zhname === this.selectedTeacher) {
          return t.stat
        }
      }
      return null
    }
  }
}
</script>

<style>
.lab-chart {
  width: 100%;
  height: 600px;
}
</style>
