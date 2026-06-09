import 'package:cloud_firestore/cloud_firestore.dart';

class Account {
  final String id;
  final String name;
  final String type; // 'stock' | 'coin'
  final double initialBalance;
  final String currency; // 'KRW' | 'USD' | 'USDT' | custom
  final DateTime createdAt;

  const Account({
    required this.id,
    required this.name,
    required this.type,
    required this.initialBalance,
    this.currency = 'KRW',
    required this.createdAt,
  });

  String get currencySymbol {
    switch (currency) {
      case 'KRW': return '₩';
      case 'USD': return '\$';
      default: return currency;
    }
  }

  factory Account.fromDoc(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return Account(
      id: doc.id,
      name: d['name'] as String,
      type: d['type'] as String,
      initialBalance: (d['initialBalance'] as num).toDouble(),
      currency: d['currency'] as String? ?? 'KRW',
      createdAt: (d['createdAt'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toMap() => {
        'name': name,
        'type': type,
        'initialBalance': initialBalance,
        'currency': currency,
        'createdAt': Timestamp.fromDate(createdAt),
      };
}
