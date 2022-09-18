<template>
  <el-container>
    <el-main style='text-align: center'>
      <template v-if='studentId == null || info == null'>
        <el-radio-group v-model='selectedTeacher'>
          <el-radio-button
            label='全部'
          ></el-radio-button>
          <el-radio-button
            v-for='t in teachers'
            :key='t.codename'
            :label='t.zhname'
          ></el-radio-button>
        </el-radio-group>
        <el-table
          class='stu-table'
          :data="filteredStudents"
          style="width: 100%"
          @row-click='studentClicked'
        >
          <el-table-column
            prop="id"
            label="学号"
            width='120px'
            sortable
          >
          </el-table-column>
          <el-table-column
            prop="name"
            label="姓名"
            sortable
          >
          </el-table-column>
        </el-table>
      </template>
      <template v-else>
        <el-descriptions>
          <el-descriptions-item label="学号">{{studentId}}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{info.name}}</el-descriptions-item>
          <!--el-descriptions-item label="教师">{{info.teacher}}</el-descriptions-item-->
        </el-descriptions>
        <el-divider></el-divider>
        <el-table :data="tableData">
          <el-table-column key='title' label='' prop='title' fixed>
          </el-table-column>
          <el-table-column
            v-for="lab in info.labs"
            :key='lab.lab'
            :label='lab.lab'
            :prop='lab.lab'
            width='170px'
          >
          </el-table-column>
        </el-table>
        <el-divider></el-divider>
      </template>
      <div
        v-show='studentId != null && info != null'
        ref="gantt"
        style='height: 600px'>
      </div>
      <el-table
        v-if='selectedLab'
        :data="selectedLab.log"
        style='margin-top: 10px'
      >
        <el-table-column
          label="时间"
          :formatter='formatLogDate'
          width='200px'
        >
        </el-table-column>
        <el-table-column
          prop="0"
          label="成绩"
          width='150px'
        >
        </el-table-column>
        <el-table-column
          label="实验"
          :formatter='() => selectedLabId'
        >
        </el-table-column>
      </el-table>
      <el-divider></el-divider>
      <el-row :style='studentId != null && info != null ? null : { opacity: 0 }'>
        <el-col v-if='info && info.stats' :span="8">
          <div id="stats-pie" style="width: 100%; height: 500px;"></div>
        </el-col>
        <el-col :span="(info && info.stats) ? 16 : 24">
          <el-descriptions v-if='stat_secs'>
            <el-descriptions-item label="总开发时间">{{stat_secs}}</el-descriptions-item>
          </el-descriptions>
          <div class='open-table'>
            <template
              v-if='info && info.opens'
            >
              <el-table-pagination
                type="local"
                style="width: 100%"
                :data="info.opens"
                :page-sizes="20"
                :columns="[
                  {
                    prop: '0',
                    label: '时间',
                    width: 30
                  }, {
                    prop: '1',
                    label: '打开文件',
                  }
                ]"
                :formOptions="{
                  style: 'width: 100%'
                }"
              >
              </el-table-pagination>
            </template>
          </div>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<style>
.open-table table {
  width: 100% !important;
}
</style>

<script>
import formatDuration from 'format-duration'
import {gantt} from 'dhtmlx-gantt'
import {formatTime} from '../util'
import 'dhtmlx-gantt/codebase/dhtmlxgantt.css'
import './gantt.css'
import * as echarts from 'echarts'
import * as humanizeDuration from 'humanize-duration'

gantt.plugins({
  marker: true,
  tooltip: true
})

function humanSecs(secs) {
  return humanizeDuration(secs * 1000, {
    language: 'zh_CN',
    delimiter: ' '
  })
}

export default {
  data() {
    return {
      selectedTeacher: '全部',
      students: null,
      teachers: null,
      info: null,
      // loading: false,
      selectedLabId: null,
      pie: null,
      stat_secs: null
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
    gantt.config.readonly = true
    gantt.config.autosize = true
    gantt.config.columns = [
      {
        name: 'text',
        label: 'Lab',
        width: 100
      }
    ]

    const zoomConfig = {
      maxColumnWidth: 500,
      levels: [
        [
          {unit: 'year', step: 1, format: '%Y'},
          {unit: 'month', step: 1, format: '%Y/%m'}
        ],
        [
          {unit: 'month', format: '%Y/%m', step: 1},
          {unit: 'week', format: '%W 周', step: 1}
        ],
        [
          {unit: 'day', format: '%m/%d', step: 1}
        ],
        {
          min_column_width: 200,
          scales: [
            {unit: 'day', format: '%m/%d', step: 1},
            {unit: 'hour', format: '%H:00 - %H:59', step: 1}
          ]
        }
      ],
      // useKey: 'altKey',
      trigger: 'wheel',

      element() {
        return gantt.$root.querySelector('.gantt_task')
      }
    }

    gantt.templates.tooltip_text = (start, end, task) => {
      const {s} = task
      return `<b>${task.text}</b><br>起始时间：${start.toLocaleString()}<br>截止时间：${end.toLocaleString()}<br>最终成绩：${s.final_score}`
    }

    gantt.ext.zoom.init(zoomConfig)
    gantt.ext.zoom.setLevel(1)
    gantt.init(this.$refs.gantt)

    gantt.attachEvent('onTaskClick', (id, e) => {
      this.selectedLabId = id
      e.value = true
      return true
    })

    const pie = echarts.init(document.getElementById('stats-pie'))
    this.pie = pie
    window.addEventListener('resize', () => pie.resize())
    pie.resize()
  },
  methods: {
    async fetch_data() {
      const id = this.studentId
      if (id) {
        const {data} = await this.$http.get(`/json/student/${id}`)
        this.info = data
        console.log(id, data)
        if (data.opens) {
          for (const row of data.opens) {
            row[0] = new Date(row[0]).toLocaleString()
          }
        }
        for (const lab of data.labs) {
          this.statLab(lab)
        }
        this.draw()
        this.$http.get(`/json/stats/${id}`).then(r => {
          console.log('got stats', r)
          if (r.data.error) {
            console.error('stats:', r.data)
            return
          }
          this.info.stats = r.data
          try {
            this.draw_pie()
          } catch (e) {
            console.error('pie:', e)
            try {
              this.stat_secs = humanSecs(this.info.stats.data.total_seconds)
            } catch (e) {}
            this.info.stats = null
          }
        })
      } else {
        const {data} = await this.$http.get(`/json/all_students`)
        this.students = data.students
        this.teachers = data.teachers
      }
    },
    studentClicked(row) {
      this.$router.push('/student/' + row.id)
      window.scrollTo(0, 0)
    },
    statLab(lab) {
      /* eslint-disable camelcase */
      let first_any = null
      let first_passed = null
      let first_full = null
      let final_score = 0
      let max_score = 0
      const begin = Date.parse(lab.begin)
      const end = Date.parse(lab.end)

      let count = 0
      for (const line of lab.log) {
        count += 1
        line[1] = new Date(line[1])
        const [score, date] = line
        const ts = date.getTime()
        if (first_any == null) {
          first_any = ts - begin
        }
        if (score >= 60 && first_passed == null) {
          first_passed = [ts - begin, count]
        }
        if (score >= 100 && first_full == null) {
          first_full = [ts - begin, count]
        }
        if (score > max_score) {
          max_score = score
          if (ts < end) {
            final_score = score
          }
        }
      }

      lab.first_any = first_any
      lab.first_passed = first_passed
      lab.first_full = first_full
      lab.final_score = final_score
      lab.max_score = max_score

      const start_date = lab.start_date = new Date(lab.begin)
      const end_date = lab.end_date = new Date(lab.end)
      lab.start_ts = start_date.getTime()
      lab.end_ts = end_date.getTime()
    },
    draw_pie() {
      if (this.info.stats) {
        this.pie.setOption({
          title: {
            text: '总开发时间：' + humanSecs(this.info.stats.data.total_seconds),
            x: 'center',
            top: 10
          },
          grid: {
            left: '0%',
            top: '0%',
            right: '0%',
            bottom: '0%'
          },
          legend: {
            orient: 'horizontal',
            bottom: 0
          },
          tooltip: {
            trigger: 'item',
            formatter: o => {
              return o.name + ': ' + humanSecs(o.data.total_seconds)
            }
          },
          series: [{
            type: 'pie',
            data: this.info.stats.data.languages.map(o => ({
              ...o,
              name: o.name === 'unknown' ? 'Text' : o.name,
              value: o.total_seconds
            })),
            label: {
              show: false
            }
          }]
        })
        this.pie.resize()
      }
    },
    draw() {
      const now = Date.now()
      gantt.templates.task_class = (_, __, task) => {
        const {s} = task
        const {final_score: score} = s
        if (score >= 100) {
          return 'task-full'
        } else if (score >= 60) {
          return 'task-passed'
        } else if (now >= s.end_ts) {
          return 'task-fail'
        } else {
          return 'task-unpassed'
        }
      }

      const data = this.info.labs.map(s => {
        const {start_ts} = s
        let progress = 0
        if (now >= start_ts) {
          const {end_ts} = s
          if (now >= end_ts) {
            progress = 1
          } else {
            progress = (now - start_ts) / (end_ts - start_ts)
          }
        }
        return {
          id: s.lab,
          text: s.lab,
          start_date: s.start_date,
          end_date: s.end_date,
          progress,
          s
        }
      })

      for (const s of this.info.labs) {
        for (const [score, time] of s.log) {
          gantt.addMarker({
            start_date: time,
            css: score >= 100 ? 'marker-full' : (score >= 60 ? 'marker-pass' : 'marker-fail'),
            title: s.lab + ', ' + score
          })
        }
      }

      gantt.parse({data})
    },
    changeGanttZoomLevel(lvl) {
      gantt.ext.zoom.setLevel(lvl)
      // gantt.render()
    },
    formatDur(millis) {
      if (isNaN(millis) || !isFinite(millis)) {
        return '-'
      }
      return formatDuration(millis)
    },
    formatLogDate(log) {
      return log[1].toLocaleString()
    }
  },
  computed: {
    studentId() {
      return this.$route.params.id
    },
    labMap() {
      const map = new Map()
      if (this.info) {
        for (const s of this.info.labs) {
          map.set(s.lab, s)
        }
      }
      return map
    },
    teacherMap() {
      const map = new Map()
      for (const t of this.teachers) {
        map.set(t.codename, t.zhname)
      }
      return map
    },
    filteredStudents() {
      if (!this.students) {
        return []
      }
      const selectedTeacher = this.selectedTeacher
      if (selectedTeacher === '全部') {
        return this.students
      }
      return this.students.filter(s => this.teacherMap.get(s.teacher) === selectedTeacher)
    },
    tableData() {
      if (!this.info) {
        return
      }
      const rows = []
      const addRow = (key, title) => {
        const o = {title}
        if (typeof key === 'string') {
          for (const t of this.info.labs) {
            o[t.lab] = t[key]
          }
        } else {
          for (const t of this.info.labs) {
            let v
            try {
              v = key(t)
            } catch (e) {
            }
            o[t.lab] = v == null ? '-' : v
          }
        }
        rows.push(o)
      }
      addRow(s => formatTime(s.begin), '起始时间')
      addRow(s => formatTime(s.end), '结束时间')
      addRow('final_score', '最终成绩')
      addRow('max_score', '最高成绩')
      addRow(s => s.log.length, '提交次数')
      addRow(s => s.first_passed[1], '首次通过提交次数')
      addRow(s => s.first_full[1], '首次满分提交次数')
      addRow(s => this.formatDur(s.first_any), '首次提交用时')
      addRow(s => this.formatDur(s.first_passed[0]), '首次通过提交用时')
      addRow(s => this.formatDur(s.first_full[0]), '首次满分提交用时')
      addRow(s => `${s.rank} (${(100 * s.rank / this.info.stu_num).toFixed(2)}%)`, '排名')

      return rows
    },
    selectedLab() {
      return this.labMap.get(this.selectedLabId)
    }
  }
}
</script>
