'use strict';

const express = require('express');

const settings = require('./config/settings');
const Database = require('./config/database');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditModel = require('./models/auditModel');
const ReportModel = require('./models/reportModel');
const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');
const buildRouter = require('./routes/routes');
const { errorHandler } = require('./middlewares/errorHandler');

/**
 * Composition root — wires config, DB, models, controllers, routes and error handling.
 * This is the ONLY place that assembles the application; no business logic lives here.
 */
async function createApp() {
  const db = new Database();
  await db.init();

  const userModel = new UserModel(db);
  const courseModel = new CourseModel(db);
  const enrollmentModel = new EnrollmentModel(db);
  const paymentModel = new PaymentModel(db);
  const auditModel = new AuditModel(db);
  const reportModel = new ReportModel(db);

  const checkoutController = new CheckoutController({
    db, userModel, courseModel, enrollmentModel, paymentModel, auditModel,
  });
  const reportController = new ReportController({ reportModel });
  const userController = new UserController({ db, userModel, enrollmentModel, paymentModel });

  const app = express();
  app.use(express.json());
  app.use(buildRouter({ checkoutController, reportController, userController }));
  app.use(errorHandler);

  return { app, db };
}

if (require.main === module) {
  createApp()
    .then(({ app }) => {
      app.listen(settings.port, () => {
        console.log(`LMS rodando na porta ${settings.port}...`);
      });
    })
    .catch((err) => {
      console.error('Falha ao iniciar a aplicação:', err);
      process.exit(1);
    });
}

module.exports = createApp;
