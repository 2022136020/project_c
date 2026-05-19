import 'package:cloud_firestore/cloud_firestore.dart';

class AccountTransaction {
  final String id;
  final String type; // 'deposit' | 'withdrawal'
  final double amount;
  final DateTime date;
  final String? note;

  const AccountTransaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.date,
    this.note,
  });

  factory AccountTransaction.fromDoc(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return AccountTransaction(
      id: doc.id,
      type: d['type'] as String,
      amount: (d['amount'] as num).toDouble(),
      date: (d['date'] as Timestamp).toDate(),
      note: d['note'] as String?,
    );
  }

  Map<String, dynamic> toMap() => {
        'type': type,
        'amount': amount,
        'date': Timestamp.fromDate(date),
        if (note != null) 'note': note,
      };
}
