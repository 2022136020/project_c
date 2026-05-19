import 'package:flutter/material.dart';
import '../../models/account.dart';
import '../../models/position.dart';
import '../../services/firestore_service.dart';
import '../position/review_screen.dart';
import '../position/close_position_screen.dart';

class DashboardScreen extends StatelessWidget {
  final List<Account> accounts;
  const DashboardScreen({super.key, required this.accounts});

  @override
  Widget build(BuildContext context) {
    final service = FirestoreService();

    return StreamBuilder<List<Position>>(
      stream: service.positionsStream(),
      builder: (context, posSnap) {
        final positions = posSnap.data ?? [];
        final open = positions.where((p) => p.status == 'open').toList();
        final closed = positions.where((p) => p.status == 'closed').toList();

        final totalPnl = closed.fold<double>(
            0, (sum, p) => sum + (p.realizedPnl ?? 0));
        final winCount = closed.where((p) => (p.returnRate ?? 0) > 0).length;
        final winRate = closed.isEmpty ? 0.0 : winCount / closed.length * 100;

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // ── 자산 현황 요약 ──────────────────────────────
            Text('자산 현황',
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            _SummaryRow(accounts: accounts, service: service),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(
                child: _StatCard(
                  label: '누적 실현 손익',
                  value:
                      '${totalPnl >= 0 ? '+' : ''}₩${_fmt(totalPnl)}',
                  valueColor: totalPnl >= 0 ? Colors.blue : Colors.red,
                  icon: Icons.trending_up,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _StatCard(
                  label: '승률',
                  value: closed.isEmpty
                      ? '-'
                      : '${winRate.toStringAsFixed(1)}%',
                  valueColor:
                      winRate >= 50 ? Colors.blue : Colors.orange,
                  icon: Icons.emoji_events_outlined,
                ),
              ),
            ]),
            Row(children: [
              Expanded(
                child: _StatCard(
                  label: '보유 포지션',
                  value: '${open.length}개',
                  icon: Icons.pending_outlined,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _StatCard(
                  label: '완료 포지션',
                  value: '${closed.length}개',
                  icon: Icons.check_circle_outline,
                ),
              ),
            ]),
            const SizedBox(height: 20),

            // ── 최근 포지션 목록 ────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('최근 포지션',
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold)),
                Text('${positions.length}개 전체',
                    style: const TextStyle(
                        color: Colors.grey, fontSize: 12)),
              ],
            ),
            const SizedBox(height: 8),
            if (positions.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Text('포지션이 없습니다.',
                      style: TextStyle(color: Colors.grey)),
                ),
              )
            else
              ...positions.take(5).map((p) => _RecentPositionTile(
                  position: p, accounts: accounts)),
          ],
        );
      },
    );
  }

  static String _fmt(double v) => v
      .abs()
      .toStringAsFixed(0)
      .replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}

// ── 계좌 잔액 합산 위젯 ──────────────────────────────────────────
class _SummaryRow extends StatelessWidget {
  final List<Account> accounts;
  final FirestoreService service;
  const _SummaryRow({required this.accounts, required this.service});

  @override
  Widget build(BuildContext context) {
    if (accounts.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text('계좌를 먼저 등록해 주세요.',
              style: TextStyle(color: Colors.grey.shade600)),
        ),
      );
    }

    return FutureBuilder<double>(
      future: Future.wait(accounts.map(
              (a) => service.calcBalance(a.id, a.initialBalance)))
          .then((list) => list.fold<double>(0.0, (a, b) => a + b)),
      builder: (context, snap) {
        final total = snap.data ?? 0.0;
        return Card(
          color: Theme.of(context).colorScheme.primaryContainer,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('총 잔액',
                    style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context).colorScheme.primary)),
                const SizedBox(height: 4),
                Text(
                  snap.hasData ? '₩${_fmt(total)}' : '...',
                  style: const TextStyle(
                      fontSize: 28, fontWeight: FontWeight.bold),
                ),
                Text('계좌 ${accounts.length}개',
                    style: const TextStyle(
                        fontSize: 12, color: Colors.grey)),
              ],
            ),
          ),
        );
      },
    );
  }

  static String _fmt(double v) => v
      .toStringAsFixed(0)
      .replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;
  final IconData icon;
  const _StatCard(
      {required this.label,
      required this.value,
      required this.icon,
      this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(icon, size: 14, color: Colors.grey),
              const SizedBox(width: 4),
              Text(label,
                  style: const TextStyle(
                      fontSize: 12, color: Colors.grey)),
            ]),
            const SizedBox(height: 6),
            Text(value,
                style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: valueColor)),
          ],
        ),
      ),
    );
  }
}

class _RecentPositionTile extends StatelessWidget {
  final Position position;
  final List<Account> accounts;
  const _RecentPositionTile(
      {required this.position, required this.accounts});

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
    final rate = position.returnRate;

    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: ListTile(
        leading: CircleAvatar(
          radius: 18,
          backgroundColor: isOpen
              ? Colors.green.shade50
              : (rate != null && rate >= 0
                  ? Colors.blue.shade50
                  : Colors.red.shade50),
          child: Icon(
            isOpen ? Icons.pending_outlined : Icons.check_circle_outline,
            size: 16,
            color: isOpen
                ? Colors.green
                : (rate != null && rate >= 0 ? Colors.blue : Colors.red),
          ),
        ),
        title: Text(position.symbol,
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(_accountName(),
            style: const TextStyle(fontSize: 11)),
        trailing: rate == null
            ? Text('₩${_fmt(position.investedAmount)}',
                style: const TextStyle(fontSize: 13))
            : Text(
                '${rate >= 0 ? '+' : ''}${rate.toStringAsFixed(2)}%',
                style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: rate >= 0 ? Colors.blue : Colors.red),
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

  static String _fmt(double v) => v
      .toStringAsFixed(0)
      .replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}
