import 'package:flutter/material.dart';
import 'package:flutter/src/widgets/container.dart';
import 'package:flutter/src/widgets/framework.dart';

class AudioButton extends StatelessWidget {
  final IconData icon;
  final Function()? onTap;

  const AudioButton({super.key, required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final icon = Icon(this.icon, color: theme.primaryColor, size: 30);

    return ClipOval(
        child: Material(
      color: theme.primaryColor.withOpacity(0.1),
      child: InkWell(
        onTap: onTap,
        child: SizedBox(width: 56, height: 56, child: icon),
      ),
    ));
  }
}
