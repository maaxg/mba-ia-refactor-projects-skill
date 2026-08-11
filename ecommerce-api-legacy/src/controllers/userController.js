'use strict';

/** User admin operations — delete now cascades in a transaction (no orphaned rows). */
class UserController {
  constructor({ db, userModel, enrollmentModel, paymentModel }) {
    this.db = db;
    this.userModel = userModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
  }

  deleteUser = async (req, res, next) => {
    try {
      const { id } = req.params;
      await this.db.transaction(async () => {
        await this.paymentModel.deleteByUserId(id);
        await this.enrollmentModel.deleteByUserId(id);
        await this.userModel.deleteById(id);
      });
      return res.json({ msg: 'Usuário e dados relacionados (matrículas, pagamentos) removidos' });
    } catch (err) {
      return next(err);
    }
  };
}

module.exports = UserController;
