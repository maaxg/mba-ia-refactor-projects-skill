'use strict';

class ReportModel {
  constructor(db) {
    this.db = db;
  }

  /**
   * Single JOIN query for the financial report — replaces the legacy N+1
   * (courses → per-course enrollments → per-enrollment user + payment).
   */
  courseFinancials() {
    return this.db.all(
      `SELECT c.id    AS course_id,
              c.title AS course,
              e.id    AS enrollment_id,
              u.name  AS student,
              p.amount AS paid,
              p.status AS status
         FROM courses c
         LEFT JOIN enrollments e ON e.course_id = c.id
         LEFT JOIN users u       ON u.id = e.user_id
         LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id, e.id`,
    );
  }
}

module.exports = ReportModel;
