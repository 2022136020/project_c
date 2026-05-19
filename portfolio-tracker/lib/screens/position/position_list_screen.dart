import 'package:flutter/material.dart';
import '../../models/account.dart';
import '../../models/position.dart';
import '../../services/firestore_service.dart';
import 'add_position_screen.dart';
import 'close_position_screen.dart';
import 'review_screen.dart';

class PositionListScreen extends StatelessWidget {
  final List<Account> accounts;
  const PositionListScreen({super.key, required this.accounts});

  @override
  Widget build(BuildContext context) {
    final service = FirestoreService();

    return StreamBuilder<List<Position>>(
      stream: service.positionsStream(),
      builder: (context, snapshot) {
        final positions = snapshot.data ?? [];
        final open = positions.where((p) => p.status == 'open').toList();
        final closed = positions.where((p) => p.status == 'closed').toList();

        return Scaffold(
          body: positions.isEmpty
              ? const Center(child: Text('포지션이 없습니다.\n우측 하단 버튼으로 추가하세요.',
                  textAlign: TextAlign.center))
              : ListView(
                  children: [
                    if (open.isNotEmpty) ...[
                      const _SectionHeader('보유 중'),
                      ...open.map((p) => _PositionTile(
                          position: p, accounts: accounts, service: service)),
                    ],
                    if (closed.isNotEmpty) ...[
                      const _SectionHeader('정리 완료'),
                      ...closed.map((p) => _PositionTile(
                          position: p, accounts: accounts, service: service)),
                    ],
                  ],
                ),
          floatingActionButton: FloatingActionButton.extended(
            onPressed: accounts.isEmpty
                ? () => ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('먼저 계좌를 등록해 주세요.')))
                : () => Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (_) =>
                            AddPositionScreen(accounts: accounts))),
            icon: const Icon(Icons.add),
            label: const Text('포지션 추가'),
          ),
        );
      },
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader(this.title);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      child: Text(title,
          style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Theme.of(context).colorScheme.primary)),
    );
  }
}

class _PositionTile extends StatelessWidget {
  final Position position;
  final List<Account> accounts;
  final FirestoreService service;
  const _PositionTile(
      {required this.position, required this.accounts, required this.service});

  String _accountName() {
    try {
      return accounts.firstWhere((a) => a.id == position.accountId).name;
    } catch (_) {
      return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    final isOpen = position.status == 'open';
    final returnRate = position.returnRate;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: position.assetType == 'stock'
              ? Colors.indigo.shade50
              : Colors.orange.shade50,
          child: Icon(
            position.assetType == 'stock'
                ? Icons.bar_chart
                : Icons.currency_bitcoin,
            color: position.assetType == 'stock'
                ? Colors.indigo
                : Colors.orange,
            size: 18,
          ),
        ),
        title: Row(
          children: [
            Text(position.symbol,
                style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: isOpen ? Colors.green.shade50 : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                isOpen ? '보유 중' : '정리',
                style: TextStyle(
                    fontSize: 11,
                    color: isOpen ? Colors.green : Colors.grey),
              ),
            ),
          ],
        ),
        subtitle: Text(
          '${_accountName()} · 진입가 ₩${_fmt(position.entryPrice)} × ${position.quantity}',
          style: const TextStyle(fontSize: 12),
        ),
        trailing: returnRate == null
            ? Text('₩${_fmt(position.investedAmount)}',
                style: const TextStyle(fontSize: 13))
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${returnRate >= 0 ? '+' : ''}${returnRate.toStringAsFixed(2)}%',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: returnRate >= 0 ? Colors.blue : Colors.red,
                    ),
                  ),
                  Text(
                    '₩${_fmt(position.realizedPnl!)}',
                    style: TextStyle(
                      fontSize: 11,
                      color: returnRate >= 0 ? Colors.blue : Colors.red,
                    ),
                  ),
                ],
              ),
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => isOpen
                ? ClosePositionScreen(position: position)
                : ReviewScreen(position: position),
          ),
        ),
      ),
    );
  }

  String _fmt(double v) => v.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}
