'use strict';

const paymentService = require('../services/paymentService');
const { hashPassword } = require('../services/password');
const { ValidationError } = require('../middlewares/errorHandler');

/**
 * Checkout flow orchestration. Business flow lives here; persistence lives in the models;
 * the whole write sequence runs in a single atomic transaction.
 */
class CheckoutController {
  constructor({ db, userModel, courseModel, enrollmentModel, paymentModel, auditModel }) {
    this.db = db;
    this.userModel = userModel;
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.auditModel = auditModel;
  }

  checkout = async (req, res, next) => {
    try {
      const { usr, eml, pwd, c_id: courseId, card } = req.body || {};
      if (!usr || !eml || !pwd || !courseId || !card) {
        throw new ValidationError('Campos obrigatórios: usr, eml, pwd, c_id, card');
      }

      const course = await this.courseModel.findActiveById(courseId);
      if (!course) {
        return res.status(404).json({ error: 'Curso não encontrado' });
      }

      const payment = paymentService.charge(card, course.price);
      if (payment.status === 'DENIED') {
        return res.status(400).json({ error: 'Pagamento recusado' });
      }

      const result = await this.db.transaction(async () => {
        let user = await this.userModel.findByEmail(eml);
        let userId;
        if (!user) {
          const created = await this.userModel.create(usr, eml, hashPassword(pwd));
          userId = created.lastID;
        } else {
          userId = user.id;
        }
        const enrollment = await this.enrollmentModel.create(userId, courseId);
        await this.paymentModel.create(enrollment.lastID, course.price, payment.status);
        await this.auditModel.create(`Checkout curso ${courseId} por ${userId}`);
        return { enrollmentId: enrollment.lastID };
      });

      return res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
      return next(err);
    }
  };
}

module.exports = CheckoutController;
