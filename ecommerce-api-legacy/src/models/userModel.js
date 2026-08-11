'use strict';

class UserModel {
  constructor(db) {
    this.db = db;
  }

  findByEmail(email) {
    return this.db.get('SELECT * FROM users WHERE email = ?', [email]);
  }

  create(name, email, passHash) {
    return this.db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passHash]);
  }

  deleteById(id) {
    return this.db.run('DELETE FROM users WHERE id = ?', [id]);
  }
}

module.exports = UserModel;
