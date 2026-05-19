import 'package:cloud_firestore/cloud_firestore.dart';

class Account {
  final String id;
  final String name;
  final String type; // 'stock' | 'coin'
  final double initialBalance;
  final DateTime createdAt;

  const Account({
    required this.id,
    required this.name,
    required this.type,
    required this.initialBalance,
    required this.createdAt,
  });

  factory Account.fromDoc(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return Account(
      id: doc.id,
      name: d['name'] as String,
      type: d['type'] as String,
      initialBalance: (d['initialBalance'] as num).toDouble(),
      createdAt: (d['createdAt'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toMap() => {
        'name': name,
        'type': type,
        'initialBalance': initialBalance,
        'createdAt': Timestamp.fromDate(createdAt),
      };
}
