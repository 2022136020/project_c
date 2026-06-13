import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/account.dart';
import '../models/transaction.dart';
import '../models/position.dart';

class FirestoreService {
  final _db = FirebaseFirestore.instance;

  String get _uid {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('로그인이 필요합니다.');
    return user.uid;
  }
  CollectionReference get _accounts => _db.collection('users/$_uid/accounts');
  CollectionReference get _positions => _db.collection('users/$_uid/positions');

  CollectionReference _transactions(String accountId) =>
      _db.collection('users/$_uid/accounts/$accountId/transactions');

  static const _timeout = Duration(seconds: 15);

  // ── 계좌 ──────────────────────────────────────────────────
  Stream<List<Account>> accountsStream() => _accounts
      .orderBy('createdAt', descending: true)
      .snapshots()
      .map((s) => s.docs.map(Account.fromDoc).toList());

  Future<void> addAccount(Account account) async =>
      await _accounts.add(account.toMap()).timeout(_timeout);

  Future<void> deleteAccount(String id) async {
    final txSnap = await _transactions(id).get().timeout(_timeout);
    final batch = _db.batch();
    for (final doc in txSnap.docs) {
      batch.delete(doc.reference);
    }
    batch.delete(_accounts.doc(id));
    await batch.commit().timeout(_timeout);
  }

  // ── 입출금 ────────────────────────────────────────────────
  Stream<List<AccountTransaction>> transactionsStream(String accountId) =>
      _transactions(accountId)
          .orderBy('date', descending: true)
          .snapshots()
          .map((s) => s.docs.map(AccountTransaction.fromDoc).toList());

  Future<void> addTransaction(String accountId, AccountTransaction tx) async =>
      await _transactions(accountId).add(tx.toMap()).timeout(_timeout);

  Future<double> calcBalance(String accountId, double initialBalance) async {
    final snap = await _transactions(accountId).get().timeout(_timeout);
    final txs = snap.docs.map(AccountTransaction.fromDoc).toList();
    double balance = initialBalance;
    for (final tx in txs) {
      balance += tx.type == 'deposit' ? tx.amount : -tx.amount;
    }
    return balance;
  }

  // ── 포지션 ────────────────────────────────────────────────
  Stream<List<Position>> positionsStream({String? accountId}) {
    Query q = _positions.orderBy('entryDate', descending: true);
    if (accountId != null) q = q.where('accountId', isEqualTo: accountId);
    return q.snapshots().map((s) => s.docs.map(Position.fromDoc).toList());
  }

  Future<void> addPosition(Position position) async =>
      await _positions.add(position.toMap()).timeout(_timeout);

  Future<void> closePosition(
      String positionId, double exitPrice, DateTime exitDate) async =>
      await _positions.doc(positionId).update({
        'exitPrice': exitPrice,
        'exitDate': Timestamp.fromDate(exitDate),
        'status': 'closed',
      }).timeout(_timeout);

  Future<void> updateReview(String positionId, String review) async =>
      await _positions.doc(positionId).update({'review': review}).timeout(_timeout);

  Future<void> deletePosition(String id) async =>
      await _positions.doc(id).delete().timeout(_timeout);
}
