import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/account.dart';
import '../models/transaction.dart';
import '../models/position.dart';

class FirestoreService {
  final _db = FirebaseFirestore.instance;

  String get _uid => FirebaseAuth.instance.currentUser!.uid;
  CollectionReference get _accounts => _db.collection('users/$_uid/accounts');
  CollectionReference get _positions => _db.collection('users/$_uid/positions');

  CollectionReference _transactions(String accountId) =>
      _db.collection('users/$_uid/accounts/$accountId/transactions');

  // ── 계좌 ──────────────────────────────────────────────────
  Stream<List<Account>> accountsStream() => _accounts
      .orderBy('createdAt', descending: true)
      .snapshots()
      .map((s) => s.docs.map(Account.fromDoc).toList());

  Future<void> addAccount(Account account) =>
      _accounts.add(account.toMap());

  Future<void> deleteAccount(String id) =>
      _accounts.doc(id).delete();

  // ── 입출금 ────────────────────────────────────────────────
  Stream<List<AccountTransaction>> transactionsStream(String accountId) =>
      _transactions(accountId)
          .orderBy('date', descending: true)
          .snapshots()
          .map((s) => s.docs.map(AccountTransaction.fromDoc).toList());

  Future<void> addTransaction(
          String accountId, AccountTransaction tx) =>
      _transactions(accountId).add(tx.toMap());

  Future<double> calcBalance(String accountId, double initialBalance) async {
    final snap = await _transactions(accountId).get();
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

  Future<void> addPosition(Position position) =>
      _positions.add(position.toMap());

  Future<void> closePosition(
      String positionId, double exitPrice, DateTime exitDate) =>
      _positions.doc(positionId).update({
        'exitPrice': exitPrice,
        'exitDate': Timestamp.fromDate(exitDate),
        'status': 'closed',
      });

  Future<void> updateReview(String positionId, String review) =>
      _positions.doc(positionId).update({'review': review});

  Future<void> deletePosition(String id) =>
      _positions.doc(id).delete();
}
