import 'package:cloud_firestore/cloud_firestore.dart';

class Position {
  final String id;
  final String accountId;
  final String symbol;
  final String assetType; // 'stock' | 'coin'
  final double entryPrice;
  final double quantity;
  final DateTime entryDate;
  final String entryReason;
  final double? targetPrice;
  final double? stopLoss;
  final double? exitPrice;
  final DateTime? exitDate;
  final String status; // 'open' | 'closed'
  final String? review;

  const Position({
    required this.id,
    required this.accountId,
    required this.symbol,
    required this.assetType,
    required this.entryPrice,
    required this.quantity,
    required this.entryDate,
    required this.entryReason,
    this.targetPrice,
    this.stopLoss,
    this.exitPrice,
    this.exitDate,
    required this.status,
    this.review,
  });

  double get investedAmount => entryPrice * quantity;

  double? get returnRate => exitPrice == null
      ? null
      : (exitPrice! - entryPrice) / entryPrice * 100;

  double? get realizedPnl => exitPrice == null
      ? null
      : (exitPrice! - entryPrice) * quantity;

  factory Position.fromDoc(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return Position(
      id: doc.id,
      accountId: d['accountId'] as String,
      symbol: d['symbol'] as String,
      assetType: d['assetType'] as String,
      entryPrice: (d['entryPrice'] as num).toDouble(),
      quantity: (d['quantity'] as num).toDouble(),
      entryDate: (d['entryDate'] as Timestamp).toDate(),
      entryReason: d['entryReason'] as String,
      targetPrice: (d['targetPrice'] as num?)?.toDouble(),
      stopLoss: (d['stopLoss'] as num?)?.toDouble(),
      exitPrice: (d['exitPrice'] as num?)?.toDouble(),
      exitDate: (d['exitDate'] as Timestamp?)?.toDate(),
      status: d['status'] as String,
      review: d['review'] as String?,
    );
  }

  Map<String, dynamic> toMap() => {
        'accountId': accountId,
        'symbol': symbol,
        'assetType': assetType,
        'entryPrice': entryPrice,
        'quantity': quantity,
        'entryDate': Timestamp.fromDate(entryDate),
        'entryReason': entryReason,
        if (targetPrice != null) 'targetPrice': targetPrice,
        if (stopLoss != null) 'stopLoss': stopLoss,
        if (exitPrice != null) 'exitPrice': exitPrice,
        if (exitDate != null) 'exitDate': Timestamp.fromDate(exitDate!),
        'status': status,
        if (review != null) 'review': review,
      };
}
