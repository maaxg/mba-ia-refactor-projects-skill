'use strict';

/** Financial report — groups the single JOIN result by course (no N+1, no manual counters). */
class ReportController {
  constructor({ reportModel }) {
    this.reportModel = reportModel;
  }

  financialReport = async (req, res, next) => {
    try {
      const rows = await this.reportModel.courseFinancials();
      const byCourse = new Map();

      for (const row of rows) {
        if (!byCourse.has(row.course_id)) {
          byCourse.set(row.course_id, { course: row.course, revenue: 0, students: [] });
        }
        const courseData = byCourse.get(row.course_id);
        if (row.enrollment_id != null) {
          if (row.status === 'PAID') {
            courseData.revenue += row.paid;
          }
          courseData.students.push({
            student: row.student || 'Unknown',
            paid: row.paid != null ? row.paid : 0,
          });
        }
      }

      return res.json(Array.from(byCourse.values()));
    } catch (err) {
      return next(err);
    }
  };
}

module.exports = ReportController;
